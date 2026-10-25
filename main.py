const { Client, GatewayIntentBits, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, ChannelType } = require('discord.js');
const { joinVoiceChannel, createAudioPlayer, createAudioResource, AudioPlayerStatus, NoSubscriberBehavior } = require('@discordjs/voice');

const client = new Client({
    intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildVoiceStates, GatewayIntentBits.GuildMembers, GatewayIntentBits.GuildMessages]
});

// --- CONFIGURA SOLO QUESTI 3 ID ---
const CANALE_ATTESA_ID = 'METTI_QUI_ID_CANALE_VOCALE_ATTESA';
const CANALE_PANNELLO_TICKET_ID = 'METTI_QUI_ID_CANALE_DOVE_VA_IL_PANNELLO';
const RUOLO_STAFF_ID = 'METTI_QUI_ID_RUOLO_STAFF';

const player = createAudioPlayer({ behaviors: { noSubscriber: NoSubscriberBehavior.Play } });
let connection = null;

client.on('ready', () => {
    console.log(`ECLISSI RP ONLINE - ${client.user.tag}`);
    inviaPannelloTicket();
});

// --- PARTE 1: ATTESA ASSISTENZA + VOCE DURA + MUSICA LOOP ---
client.on('voiceStateUpdate', async (oldState, newState) => {
    if (newState.channelId === CANALE_ATTESA_ID && !newState.member.user.bot) {
        connection = joinVoiceChannel({
            channelId: CANALE_ATTESA_ID,
            guildId: newState.guild.id,
            adapterCreator: newState.guild.voiceAdapterCreator,
            selfDeaf: false
        });
        const voce = createAudioResource('./musica/voce-attesa.mp3');
        player.play(voce);
        connection.subscribe(player);
        player.once(AudioPlayerStatus.Idle, () => playMusicaLoop());
    }
    if (oldState.channelId === CANALE_ATTESA_ID) {
        const channel = await client.channels.fetch(CANALE_ATTESA_ID);
        if (channel.members.filter(m => !m.user.bot).size === 0) {
            player.stop();
            if (connection) { connection.destroy(); connection = null; }
        }
    }
});

function playMusicaLoop() {
    const musica = createAudioResource('./musica/inno-eclissi.mp3', { inlineVolume: true });
    musica.volume.setVolume(0.12);
    player.play(musica);
    connection.subscribe(player);
    player.once(AudioPlayerStatus.Idle, () => playMusicaLoop());
}

// --- PARTE 2: PANNELLO TICKET ---
async function inviaPannelloTicket() {
    const channel = await client.channels.fetch(CANALE_PANNELLO_TICKET_ID);
    const embed = new EmbedBuilder()
        .setTitle('ECLISSI RP | CENTRO ASSISTENZA')
        .setDescription('Benvenuto su Eclissi. Seleziona il motivo per cui vuoi aprire un ticket.\nNon aprire ticket a caso o verrai sanzionato.')
        .setColor(0x2B2D31);

    const row = new ActionRowBuilder().addComponents(
        new ButtonBuilder().setCustomId('ticket_whitelist').setLabel('Cittadinanza / Whitelist').setEmoji('🪪').setStyle(ButtonStyle.Secondary),
        new ButtonBuilder().setCustomId('ticket_armi').setLabel('Porto d\'Armi').setEmoji('🔫').setStyle(ButtonStyle.Secondary),
        new ButtonBuilder().setCustomId('ticket_partner').setLabel('Partnership').setEmoji('🤝').setStyle(ButtonStyle.Secondary),
        new ButtonBuilder().setCustomId('ticket_supporto').setLabel('Supporto / Bug').setEmoji('🛠️').setStyle(ButtonStyle.Secondary),
    );
    const oldMsgs = await channel.messages.fetch({ limit: 10 });
    oldMsgs.forEach(m => { if (m.author.id === client.user.id) m.delete().catch(()=>{}); });
    channel.send({ embeds: [embed], components: [row] });
}

client.on('interactionCreate', async i => {
    if (!i.isButton()) return;
    if (!i.customId.startsWith('ticket_')) return;

    const guild = i.guild;
    const tipo = i.customId.replace('ticket_', '');
    
    let nomeCanale = `${tipo}-${i.user.username}`;
    let messaggioTicket = '';

    if (tipo === 'whitelist') {
        messaggioTicket = `**Whitelist - ECLISSI RP**\nCiao ${i.user}, per entrare rispondi con parole tue:\n1. Cos'è RDM, VDM, FearRP per te?\n2. Quando puoi sparare a qualcuno?\n3. Cosa fai se un player è a terra?\n\nSe sbagli qualcosa ti aiutiamo, non banniamo per un errore. Copiare dal regolamento = bocciato.`;
    } else if (tipo === 'armi') {
        messaggioTicket = `**Porto d'Armi - ECLISSI RP**\nCiao ${i.user}, rispondi:\n1. Quando puoi usare un'arma?\n2. Cos'è il FearRP?\n3. Perché vuoi il porto?\n\nSe sai quando NON sparare, sei promosso.`;
    } else if (tipo === 'partner') {
        messaggioTicket = `**Partnership - ECLISSI RP**\nCiao ${i.user}, invia:\n- Nome Server:\n- Link Invite (no scadenza):\n- Membri:\n- Cosa offrite / volete\n\nRequisiti: 50+ membri. Offriamo canale dedicato + ping.`;
    } else {
        messaggioTicket = `**Supporto - ECLISSI RP**\nCiao ${i.user}, descrivi il problema con prove (foto/video). Sii chiaro.`;
    }

    const canale = await guild.channels.create({
        name: nomeCanale,
        type: ChannelType.GuildText,
        parent: guild.channels.cache.get(CANALE_PANNELLO_TICKET_ID)?.parentId,
        permissionOverwrites: [
            { id: guild.id, deny: ['ViewChannel'] },
            { id: i.user.id, allow: ['ViewChannel', 'SendMessages'] },
            { id: RUOLO_STAFF_ID, allow: ['ViewChannel', 'SendMessages'] },
        ]
    });

    const embedTicket = new EmbedBuilder().setDescription(messaggioTicket).setColor(0x2B2D31);
    const rowClose = new ActionRowBuilder().addComponents(new ButtonBuilder().setCustomId('chiudi_ticket').setLabel('Chiudi Ticket').setStyle(ButtonStyle.Danger));

    await canale.send({ content: `${i.user} <@&${RUOLO_STAFF_ID}>`, embeds: [embedTicket], components: [rowClose] });
    await i.reply({ content: `Ticket aperto: ${canale}`, ephemeral: true });
    
    if (tipo === 'whitelist' || tipo === 'armi') {
        await canale.send(`> **AI ECLISSI:** Controllerò se hai copiato dal regolamento. Se rispondi con parole tue sei OK anche se non perfetto.`);
    }
});

client.on('interactionCreate', async i => {
    if (i.customId === 'chiudi_ticket') {
        await i.reply({ content: 'Chiudo in 3 secondi...' });
        setTimeout(() => i.channel.delete().catch(()=>{}), 3000);
    }
});

client.login('IL_TUO_TOKEN_QUI');