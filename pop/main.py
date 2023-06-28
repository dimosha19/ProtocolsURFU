import email
import os
import poplib
from email.header import decode_header


def write_attch(file_name, file):
    os.makedirs('attachments', exist_ok=True)
    filepath = os.path.join('attachments', file_name).replace("\"", "")
    with open(filepath, 'wb') as f:
        f.write(file)


def last_msg(server, port, username, password):
    pop_server = poplib.POP3_SSL(server, port)
    pop_server.user(username)
    pop_server.pass_(password)

    num_msg = len(pop_server.list()[1])

    if num_msg == 0:
        print("No messages.")
        return

    msg = email.message_from_bytes(b'\n'.join(pop_server.retr(num_msg)[1]))
    pop_server.quit()
    return msg


def parser(msg):
    subject = decode_header(msg.get('Subject'))[0]
    if subject[1]:
        subject = subject[0].decode(subject[1])
    sender = decode_header(msg.get('From'))[0]
    if sender[1]:
        sender = sender[0].decode(sender[1])
    date = decode_header(msg.get('Date'))[0]
    if date[1]:
        date = date[0].decode(date[1])
    msg_body = ""

    if msg.is_multipart():
        for trunc in msg.walk():
            content_type = trunc.get_content_type()
            if content_type in ["text/plain", "text/html"]:
                body = trunc.get_payload(decode=True)
                msg_body += body.decode()
            elif content_type in ["image/png", "image/jpg"]:
                file_name = decode_header(trunc.get("Content-Disposition"))[1]
                if file_name[1]:
                    file_name = file_name[0].decode(file_name[1])
                if file_name:
                    file = trunc.get_payload(decode=True)
                    write_attch(file_name, file)
    else:
        msg_body = msg.get_payload(decode=True)

    print(f"Отправитель: {sender}\nТема: {subject}\nПисьмо: {msg_body[5:-6]}\nДата: {date}\n")


if __name__ == "__main__":
    username = input("введите логин:")
    password = input("введите пароль:")
    msg = last_msg('pop.yandex.com', 995, username, password)
    if msg:
        parser(msg)
    else:
        exit(1)
"""
dimitri.shilnikov@yandex.ru
fgswrrqqypxasrrc

"""
