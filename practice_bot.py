import mysql.connector
import logging
import random
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup,BotCommandScopeAllChatAdministrators, BotCommand,WebAppInfo
from telegram.ext import Application,CommandHandler, CallbackContext, CallbackQueryHandler




#Log(Exceptions, Warnings, and Logging)
logging.basicConfig(
    level=logging.INFO
)

tg_token ="7284683751:AAH-9QfBxHSApP_XAFeI2NOBjK_B9flbE1o"

#사용자 정보들(추후 뽑기에 사용)
candidates=set()

#사용자 ID와 메시지 ID를 저장할 딕셔너리(버튼을 클릭했을 때 클릭한 사람에게만 다른 화면이 뜨게 하기 위해서)
user_messages={}

#관리자만 사용할 수 있는 명령어 scope
scope_admin=BotCommandScopeAllChatAdministrators()

#관리자만 사용할 수 있는 명령어 집합
commands=[
    BotCommand(command='start', description="Gift Event Start"),
    BotCommand(command='pick', description="Random Selection"),
    BotCommand(command='progress', description="How many people")
]

#MySQL 데이터베이스 설정
db_config={
    'host': 'giftbot-database.cc0lokhfxaeb.us-east-2.rds.amazonaws.com',
    'user': 'admin',
    'password': 'junemoiscute',
    'database': 'giftbot'
}


###########명령어############


#참여버튼
async def start(update: Update, context: CallbackContext)->None:
    
    
    url="https://giftbot-ui.vercel.app/"
    keyboard=[
        [
            InlineKeyboardButton("참여",url=url)
        ]
    ]
    reply_markup=InlineKeyboardMarkup(keyboard)
    
    user=update.effective_user
    chat=update.effective_chat
    member=await chat.get_member(user.id)

    #관리자만 명령어실행가능
    if member.status in ['administrator','creator']:
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="참여신청",
            reply_markup=reply_markup
        )
    else:
        return






#무작위 뽑기
async def pick(update: Update, context: CallbackContext) -> None:

    user=update.effective_user
    chat=update.effective_chat
    member=await chat.get_member(user.id)

    #관리자만 명령어실행가능
    if member.status in ['administrator','creator']:
        conn=mysql.connector.connect(**db_config)
        cursor=conn.cursor(dictionary=True)

        #참가자 목록을 가져오기
        cursor.execute('SELECT * FROM participants')
        results=cursor.fetchall()

        if not results:
            await update.message.reply_text("아직 참여한 사용자가 없습니다.")
            conn.close()
            return
    
        chosen_user=random.choice(results)
        await update.message.reply_text(f"{chosen_user['phoneNumber']}님 축하드립니다!! 당첨되셨습니다.")
        

        #연결 종료
        conn.close()
    else:
        return

    

'''
#참가인원 보기
async def progress(update: Update, context: CallbackContext) -> None:
    user=update.effective_user
    chat=update.effective_chat
    member=await chat.get_member(user.id)

    #관리자만 명령어실행가능
    if member.status in ['administrator','creator']:
        await update.message.reply_text(f"{len(candidates)}명이 참여하셨습니다")

'''
###################################



def main()->None:
    application=Application.builder().token(tg_token).build()
    application.bot.set_my_commands(commands=commands, scope=scope_admin)
    application.add_handler(CommandHandler("start",start))
    #application.add_handler(CallbackQueryHandler(join,pattern='join'))
    application.add_handler(CommandHandler("pick",pick))
    #application.add_handler(CommandHandler("progress",progress))

    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__== "__main__":
    main()


