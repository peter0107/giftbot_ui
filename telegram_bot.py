import mysql.connector
import logging
import random
from typing import Optional, Tuple
from telegram import Chat, ChatMember, ChatMemberUpdated, Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup,BotCommandScopeAllChatAdministrators, BotCommand,WebAppInfo
from telegram.ext import Application,CommandHandler, ContextTypes, CallbackContext, CallbackQueryHandler,ChatMemberHandler




#Log(Exceptions, Warnings, and Logging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

tg_token ="7284683751:AAH-9QfBxHSApP_XAFeI2NOBjK_B9flbE1o"


#MySQL 데이터베이스 설정
db_config={
    'host': 'giftbot-database.cc0lokhfxaeb.us-east-2.rds.amazonaws.com',
    'user': 'admin',
    'password': 'junemoiscute',
    'database': 'giftbot'
}

#group_chat_id=-4266962896


#########################계속 돌아가는 프로세스#############################

#old member와 new member를 비교해서 status 변화를 추적
def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member

#봇이 어떤 그룹에 들어가고 나가는 걸 추적
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tracks the chats the bot is in."""
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    # Let's check who is responsible for the change
    cause_name = update.effective_user.full_name

    # Handle chat types differently:
    chat = update.effective_chat
    
    if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logger.info("%s added the bot to the group %s", cause_name, chat.title)
            await add_group(chat.id, chat.title)
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s removed the bot from the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
    elif chat.type == Chat.CHANNEL:
        if not was_member and is_member:
            logger.info("%s added the bot to the channel %s", cause_name, chat.title)
            await add_group(chat.id, chat.title)
            context.bot_data.setdefault("channel_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s removed the bot from the channel %s", cause_name, chat.title)
            context.bot_data.setdefault("channel_ids", set()).discard(chat.id)
    
    

#add group id to bot_groups
async def add_group(group_id, group_name):
    try:
        # MySQL 데이터베이스에 연결
        #MySQL 데이터베이스 설정
        
        conn=mysql.connector.connect(**db_config)
        cursor=conn.cursor(dictionary=True)
        cursor = conn.cursor()

        # 테이블 생성 쿼리 작성
        cursor.execute("""
            INSERT IGNORE INTO bot_groups (group_id, group_name) VALUES (%s, %s)
        """, (group_id, group_name))
        conn.commit()

        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")



##################################################################

###########편의성############

async def get_admin_groups(context, user_id, db_config):
    # MySQL database에서 group_name과 group_id 가져오기
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT group_name, group_id FROM bot_groups")
        groups = cursor.fetchall()
        logger.info(groups)
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

    # 사용자가 관리자인 그룹 필터링
    admin_groups = []
    for group in groups:
        try:
            administrators = await context.bot.get_chat_administrators(group['group_id'])
            if any(admin.user.id == user_id for admin in administrators):
                admin_groups.append((group['group_name'], group['group_id']))
        except Exception as e:
            logger.error(f"An error occurred while checking admin status: {e}")

    return admin_groups

###########################################


###########명령어############


#어떤 그룹에 참여링크를 전달할 지 결정(테스트중)
async def start(update: Update, context: CallbackContext)->None:
    
    user=update.effective_user
    chat=update.effective_chat

    chat_id=update.message.chat_id
    user_id=update.message.from_user.id
    #member=await chat.get_member(user.id)

    admin_groups=await get_admin_groups(context,user_id,db_config)


    # 관리자인 그룹만 인라인 키보드로 제공

    if not admin_groups:
        await context.bot.send_message(chat_id=chat_id, text="관리자로 참여 중인 그룹이 없습니다")
    else:

        keyboard=[
            [InlineKeyboardButton(group_name,callback_data=f"join_{group_id}")]
            for group_name, group_id in admin_groups
        ]
        reply_markup=InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="그룹 혹은 채널을 선택하세요: ", reply_markup=reply_markup)


    #await context.bot.send_message(chat_id=group_chat_id,text="참여신청",reply_markup=reply_markup)

    #await update.message.reply_text("그룹 채팅방으로 메세지가 포워딩되었습니다.")
    '''
    #관리자만 명령어실행가능
    if member.status in ['administrator','creator']:
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="참여신청",
            reply_markup=reply_markup
        )
    else:
        return
    '''

#해당 그룹에 참여링크 보냄(테스트중)
async def game_start(update: Update, context: CallbackContext):
    query=update.callback_query
    await query.answer()

    #선택된 그룹 ID 추출
    group_id=query.data.split('_')[1]

    particp_url=f"https://giftbot-ui.vercel.app/?group_id={group_id}"
    keyboard=[
        [
            InlineKeyboardButton("참여",url=particp_url)
        ]
    ]
    particp_reply_markup=InlineKeyboardMarkup(keyboard)

    try:
        conn=mysql.connector.connect(**db_config)
        cursor=conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM participants WHERE group_id = %s",(group_id,))
        conn.commit()
        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"데이터베이스 오류 발생: {e}")



    

    #참여링크 전송(해당 그룹으로)
    try:
        await context.bot.send_message(chat_id=group_id,text="참여신청",reply_markup=particp_reply_markup)
    
    except Exception as e:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"오류 발생: {e}")





#무작위 뽑기(테스트완)

async def pick(update: Update, context: CallbackContext) -> None:

    user=update.effective_user
    chat=update.effective_chat
    chat_id=update.message.chat_id
    user_id=update.message.from_user.id

    #사용자가 admin으로 있는 그룹 or 채널
    admin_groups=await get_admin_groups(context,user_id,db_config)

    keyboard=[
        [InlineKeyboardButton(group_name,callback_data=f"pick_{group_id}")]
        for group_name, group_id in admin_groups
    ]
    reply_markup=InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text="무작위로 뽑을 그룹을 선택하세요: ", reply_markup=reply_markup)
    


async def pick_start(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    group_id = query.data.split('_')[1]

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT nickName FROM participants WHERE group_id = %s", (group_id,))
        participants = cursor.fetchall()

        if participants:
            selected_participant = random.choice(participants)
            nickname = selected_participant['nickName']

            # 선택된 참가자 정보를 암호화하여 URL 파라미터로 전달
            import base64
            encoded_winner = base64.urlsafe_b64encode(nickname.encode()).decode()

            roulette_url = f"https://giftbot-ui.vercel.app/roulette?group_id={group_id}&winner={encoded_winner}"
            keyboard = [
                [InlineKeyboardButton("결과 확인", url=roulette_url)]
            ]
            roulette_reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(chat_id=group_id, text=f"당첨자가 선정되었습니다. 결과를 확인해주세요!", reply_markup=roulette_reply_markup)
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="해당 그룹에 참가자가 없습니다.")
        
        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"데이터베이스 오류 발생: {e}")

        





#참가인원 보기

async def progress(update: Update, context: CallbackContext) -> None:

    user=update.effective_user
    chat=update.effective_chat
    chat_id=update.message.chat_id
    user_id=update.message.from_user.id

    #사용자가 admin으로 있는 그룹 or 채널
    admin_groups=await get_admin_groups(context,user_id,db_config)

    keyboard=[
        [InlineKeyboardButton(group_name,callback_data=f"progress_{group_id}_{chat_id}")]
        for group_name, group_id in admin_groups
    ]
    reply_markup=InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text="그룹 혹은 채널을 선택하세요: ", reply_markup=reply_markup)
    

async def progress_start(update: Update, context: CallbackContext) -> None:
    
    query=update.callback_query
    await query.answer()


    #선택된 그룹 ID, 현재 chat ID 추출
    group_id=query.data.split('_')[1]
    chat_id=query.data.split('_')[2]
    #참여자 닉네임 가져와서 랜덤뽑기진행
    try:
        conn=mysql.connector.connect(**db_config)
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total_records FROM participants WHERE group_id = %s", (group_id,))
        
        result=cursor.fetchone()
        count=result['total_records']
        
        cursor.close()
        conn.close()

        await context.bot.send_message(chat_id=chat_id, text=f"{count}명이 참가중입니다")

    
    except mysql.connector.Error as e:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"데이터베이스 오류 발생: {e}")
###################################



def main()->None:
    application=Application.builder().token(tg_token).build()
    #application.bot.set_my_commands(commands=commands, scope=scope_admin)

    #항상작동
    application.add_handler(ChatMemberHandler(track_chats,ChatMemberHandler.MY_CHAT_MEMBER))

    #/start
    application.add_handler(CommandHandler("start",start))
    application.add_handler(CallbackQueryHandler(game_start,pattern='^join_'))

    #/pick
    application.add_handler(CommandHandler("pick",pick))
    application.add_handler(CallbackQueryHandler(pick_start,pattern='^pick_'))

    #/progress
    application.add_handler(CommandHandler("progress",progress))
    application.add_handler(CallbackQueryHandler(progress_start,pattern='^progress_'))

    #running
    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__== "__main__":
    main()


