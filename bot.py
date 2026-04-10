npm init -y
npm install node-telegram-bot-api axios dotenv

BOT_TOKEN=8693738884:AAHwTgSJmk5-IP2sGo54pTPMb56M4MmxR3M
ADMIN_ID=@shg33
OPENAI_API_KEY=你的OpenAIKey（可选）

require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');

const bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true });

// ====== 配置 ======
const ADMIN_ID = Number(process.env.ADMIN_ID);
let AI_ENABLED = true;
let FLIRT_MODE = true;

// ====== 工具函数 ======
function isAdmin(userId) {
    return userId === ADMIN_ID;
}

// ====== 菜单按钮 ======
function getMainMenu() {
    return {
        reply_markup: {
            keyboard: [
                ["📌 打卡", "🌐 翻译"],
                ["🤖 AI聊天", "😏 反撩模式"],
                ["⚙️ 管理菜单"]
            ],
            resize_keyboard: true
        }
    };
}

// ====== 打卡按钮 ======
function getCheckInMenu() {
    return {
        reply_markup: {
            keyboard: [
                ["📊 查看记录", "🎯 今日状态"],
                ["🏠 返回主菜单"]
            ],
            resize_keyboard: true
        }
    };
}

// ====== 启动 ======
bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, "👋 欢迎使用智能机器人", getMainMenu());
});

// ====== 管理菜单 ======
bot.on("message", async (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text;
    const userId = msg.from.id;

    if (!text) return;

    // ===== 管理员菜单 =====
    if (text === "⚙️ 管理菜单") {
        if (!isAdmin(userId)) {
            return bot.sendMessage(chatId, "❌ 你没有权限");
        }

        return bot.sendMessage(chatId, "⚙️ 管理功能", {
            reply_markup: {
                keyboard: [
                    ["开关AI", "开关反撩"],
                    ["返回主菜单"]
                ],
                resize_keyboard: true
            }
        });
    }

    if (text === "开关AI" && isAdmin(userId)) {
        AI_ENABLED = !AI_ENABLED;
        return bot.sendMessage(chatId, `🤖 AI已${AI_ENABLED ? "开启" : "关闭"}`);
    }

    if (text === "开关反撩" && isAdmin(userId)) {
        FLIRT_MODE = !FLIRT_MODE;
        return bot.sendMessage(chatId, `😏 反撩模式已${FLIRT_MODE ? "开启" : "关闭"}`);
    }

    // ===== 返回主菜单 =====
    if (text === "🏠 返回主菜单") {
        return bot.sendMessage(chatId, "🏠 主菜单", getMainMenu());
    }

    // ===== 打卡 =====
    if (text === "📌 打卡") {
        bot.sendMessage(chatId, "✅ 打卡成功！（迟到也记录）");

        // 自动弹出多功能按钮
        return bot.sendMessage(chatId, "📊 请选择操作：", getCheckInMenu());
    }

    // ===== 翻译 =====
    if (text.startsWith("翻译 ")) {
        const content = text.replace("翻译 ", "");

        try {
            const res = await axios.get(`https://api.mymemory.translated.net/get?q=${content}&langpair=zh|en`);
            return bot.sendMessage(chatId, `🌐 翻译结果：\n${res.data.responseData.translatedText}`);
        } catch {
            return bot.sendMessage(chatId, "❌ 翻译失败");
        }
    }

    // ===== AI聊天 =====
    if (text === "🤖 AI聊天") {
        return bot.sendMessage(chatId, "💬 直接输入内容即可聊天");
    }

    // ===== 反撩模式 =====
    if (text === "😏 反撩模式") {
        return bot.sendMessage(chatId, "😏 来试试撩我？");
    }

    // ===== 智能回复 =====
    if (AI_ENABLED) {
        let reply = "";

        // ===== 反撩逻辑 =====
        if (FLIRT_MODE) {
            const flirtReplies = [
                "你这样说，是不是喜欢我？😏",
                "我劝你别撩，我会当真的 ❤️",
                "再说一遍，我就心动了",
                "你这句话，有点危险哦～",
                "你这是在暗示我吗？"
            ];
            reply = flirtReplies[Math.floor(Math.random() * flirtReplies.length)];
        }

        // ===== GPT 接入（可选）=====
        if (process.env.OPENAI_API_KEY) {
            try {
                const res = await axios.post("https://api.openai.com/v1/chat/completions", {
                    model: "gpt-4o-mini",
                    messages: [{ role: "user", content: text }]
                }, {
                    headers: {
                        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`
                    }
                });

                reply = res.data.choices[0].message.content;
            } catch {
                reply = reply || "🤖 我在思考中...";
            }
        }

        return bot.sendMessage(chatId, reply);
    }
});