import os, pwd, grp


def read_from_pipe(pipe):
    message = b''
    while True:
        data = os.read(pipe, 1)
        if data == b'\0':
            return message.decode('utf-8')
        else:
            message += data


def write_to_pipe(pipe, data):
    os.write(pipe, (data + "\0").encode('utf-8'))


def drop_privileges(uid_name, gid_name):
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    os.setgroups([])

    os.setgid(running_gid)
    os.setuid(running_uid)


def yes_no_prompt(question):
    yes_options = ['yes', 'y', '']
    print(question)
    choice = input()

    if choice.lower() in yes_options:
        return True
    else:
        return False
