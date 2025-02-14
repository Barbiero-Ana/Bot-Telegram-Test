import logging
import smtplib
import json
from email.message import EmailMessage
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from sentimento_analise import analisar  
import os
from dotenv import load_dotenv

load_dotenv()
# criei um arquivo .env para deixar os dados ''sigilosos'''

email_user = os.getenv('EMAIL_USER')
pass_email = os.getenv('EMAIL_PASSWORD')
token_bot = os.getenv('BOT_TOKEN')

if not all([email_user, pass_email, token_bot]):
    print("Erro: Variáveis de ambiente não encontradas!")
    exit(1)

cupom_desconto = set()

try:
    with open('logfile.json', "r") as arquivo:
        try:
            cupom_desconto = set(json.load(arquivo))
        except json.JSONDecodeError:
            cupom_desconto = set()
except FileNotFoundError:
    pass

def enviar_email(destinatario, assunto, corpo):
    try:
        msg = EmailMessage()
        msg["Subject"] = assunto
        msg["From"] = email_user
        msg["To"] = destinatario
        msg.set_content(corpo)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, pass_email)
            server.send_message(msg)
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def salvar_log():
    with open('logfile.json', "w") as arquivo:
        json.dump(list(cupom_desconto), arquivo)

async def mensagem(update: Update, context: CallbackContext):
    texto_usuario = update.message.text
    if not texto_usuario.strip():
        await update.message.reply_text("Você não enviou nenhuma mensagem. Por favor, tente novamente.")
        return

    sentimento = analisar(texto_usuario)

    if sentimento == "Positivo":
        resposta = "Que ótimo saber que você está satisfeito! Agradecemos pelo seu feedback! 😊"
    elif sentimento == "Negativo":
        resposta = "Lamentamos muito pelo ocorrido. Por favor, informe seu email para que possamos enviar um cupom de desconto como forma de desculpas."
    else:
        resposta = "Entendi! Se precisar de algo, estou aqui para ajudar."

    await update.message.reply_text(resposta)
    salvar_log()
    enviar_email(email_user, "Novo feedback recebido", f"Sentimento: {sentimento}\nMensagem: {texto_usuario}")

async def coletar_email(update: Update, context: CallbackContext):
    email = update.message.text
    if email in cupom_desconto:
        await update.message.reply_text("Já enviamos um cupom para esse email anteriormente. 😉")
    else:
        cupom_desconto.add(email)
        enviar_email(email, "Cupom de Desconto", "Aqui está seu cupom: DESCONTO10!")
        await update.message.reply_text("Cupom enviado para seu email! 🏷️")

    salvar_log()

async def ajuda(update: Update, context: CallbackContext):
    mensagem = (
        "/sentimento - analisaremos o sentimento do seu feedback\n"
        "/cupom - te enviaremos um cupom de desconto pelo e-mail digitado\n"
        "/ajuda - Exibe esta mensagem"
    )
    await update.message.reply_text(mensagem)

async def start(update: Update, context: CallbackContext):
    mensagem = (
        "Olá! Eu sou um bot de Atendimento ao Cliente.\n\n"
        "💬 Envie uma mensagem e eu analisarei seu sentimento!\n\n"
        "📩 Se for um problema, posso enviar um cupom de desconto.\n\n"
        "📝 Digite seu email caso precise do cupom.\n\n"
        "/ajuda - exibe a central de ajuda e comandos"
    )
    await update.message.reply_text(mensagem)

async def sentimento(update: Update, context: CallbackContext):
    await update.message.reply_text("Por favor, envie o seu feedback para análise do sentimento.")

EMAIL = 1

async def solicitar_email(update: Update, context: CallbackContext):
    await update.message.reply_text("Diga-me seu email para que eu possa te enviar um cupom de desconto.")
    return EMAIL

async def processar_email(update: Update, context: CallbackContext):
    email = update.message.text
    if email in cupom_desconto:
        await update.message.reply_text("Já enviamos um cupom para esse email anteriormente. 😉")
    else:
        cupom_desconto.add(email)
        enviar_email(email, "Cupom de Desconto", "Aqui está seu cupom: DESCONTO10!")
        await update.message.reply_text("Cupom enviado para seu email! 🏷️")

    salvar_log()
    return ConversationHandler.END

async def cancelar(update: Update, context: CallbackContext):
    await update.message.reply_text("Processo de cupom cancelado.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(token_bot).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('cupom', solicitar_email)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, processar_email)]
        },
        fallbacks=[CommandHandler('cancelar', cancelar)]
    )

    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sentimento", sentimento))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensagem))
    app.add_handler(MessageHandler(filters.Regex(r"^[\w\.-]+@[\w\.-]+\.\w+$"), coletar_email))

    print("Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
