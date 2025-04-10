const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { exec } = require('child_process');

const client = new Client({
    authStrategy: new LocalAuth()
});

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✅ WhatsApp Bot is ready!');
});

client.on('message', message => {
    const msg = message.body.toLowerCase();
    console.log("📩 Pesan diterima:", msg); // Tambahkan log ini

    if (msg.includes("luas panen")) {
        console.log("🧠 Menjalankan ChatBot.py...");
        exec(`python "G:/My Drive/Python/ChatBot/ChatBot.py" "${msg}"`, (error, stdout, stderr) => {
            if (error) {
                console.error(`❌ exec error: ${error}`);
                message.reply("❌ Terjadi error di bot.");
                return;
            }
            console.log("📤 Balasan:", stdout);
            message.reply(stdout);
        });
    } else {
        console.log("⚠️ Pesan tidak memicu bot.");
    }
});


client.initialize();
