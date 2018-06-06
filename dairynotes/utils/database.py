import sqlite3   #enable control of an sqlite database
import hashlib
import uuid
import os

'''f=os.path.dirname(__file__) or '.'
    f+="/../data/app.db"
    db = sqlite3.connect(f)
    c = db.cursor()

    #insert code
    
    db.commit()
    db.close()'''

#functions to write:
#edit note content
#edit title
#delete note
#change color
#change to list
#change to notlist
#check boxes
#uncheck boxes
#pin
#unpin
#archive
#unarchive
#create new label
#add label to note
#remove label
#add reminder
#remove reminder
#add image
#remove image

#==========================================================
'''
TABLE CREATION
Database
'''

def table_creation():
    f=os.path.dirname(__file__) or '.'
    f+="/../data/app.db"
    db = sqlite3.connect(f) #open if f exists, otherwise create
    c = db.cursor()         #facilitates db ops

    #Create the users table
    user_table = 'CREATE TABLE users (username TEXT PRIMARY KEY, password BLOB);'
    c.execute(user_table)

    #Create the notes table
    notes_table = 'CREATE TABLE notes (note_id INTEGER PRIMARY KEY, username TEXT, note_title TEXT, note_type TEXT, order_id INTEGER, color TEXT, pinned BOOLEAN, archived BOOLEAN, reminder_time DATETIME, reminder_repeat TEXT, image TEXT);'
    c.execute(notes_table)

    #Create the labels table
    labels_table = 'CREATE TABLE labels (note_id INTEGER, label TEXT);'
    c.execute(labels_table)

    #Create the list table
    list_table = 'CREATE TABLE list (note_id INTEGER, item TEXT, item_num INTEGER, checked BOOLEAN);'
    c.execute(list_table)

    #Create the notlist table
    notlist_table = 'CREATE TABLE notlist (note_id INTEGER, content TEXT);'
    c.execute(notlist_table)

    db.commit()
    db.close()

    
#USER TABLE STUFF

def hash_password(password):
    key = uuid.uuid4().hex
    return hashlib.sha256(key.encode() + password.encode()).hexdigest()+':' + key

def check_password(hashed_password, user_password):
    password, key = hashed_password.split(':')
    return password == hashlib.sha256(key.encode()+user_password.encode()).hexdigest()

#add a user to user table
def add_user(new_username, new_password):
    f=os.path.dirname(__file__) or '.'
    f+="/../data/app.db"
    db = sqlite3.connect(f) #open if f exists, otherwise create
    c = db.cursor()         #facilitates db ops

    hash_pass = hash_password(new_password)
    print ('The string to store in the db is: ' + hash_pass)
    c.execute('INSERT INTO users VALUES (?,?)',[new_username, hash_pass])
    db.commit()
    db.close()

#if username exist, return true
def check_username(userN):
    f=os.path.dirname(__file__) or '.'
    f+="/../data/app.db"
    db = sqlite3.connect(f)
    c = db.cursor()
    users = c.execute('SELECT username FROM users;')
    result = False
    for x in users:
        if (x[0] == userN):
            result = True
    db.close()
    return result

#checks if login is valid (username must exist and password must match to return True)
def check_login(username, password):
    f=os.path.dirname(__file__) or '.'
    f+="/../data/app.db"
    db = sqlite3.connect(f)
    c = db.cursor()

    command = 'SELECT password FROM users WHERE username="' + username + '";'
    info = c.execute(command)

    hash_pass = ''
    
    for passes in info:
        hash_pass = passes[0]

    if hash_pass == '':
        return False
    
    db.close()

    return check_password(hash_pass, password)

#NOTES TABLE STUFF

#adds a note to table
#reminder_time MUST be in format "yyyy-mm-dd hh:mm:ss"
#pinned and archived are booleans, username, note_title, note_type, color, remider_repeat, and image (link) are strings
#note_type is either "list" or "notlist"
#content is a list if note_type is a list, and a string if note_type is notlist
#checked_items is a list of Trues and False indicating which checkboxes have been checked (for lists only)

#does not catch errors in input yet
def add_note(username, note_title, note_type, color, pinned, archived, content, reminder_time=None, reminder_repeat=None, checked_items=None, image=None):
    f=os.path.dirname(__file__) or '.'    
    f+="/../data/app.db"
    db = sqlite3.connect(f)
    c = db.cursor()

    #gets next id for note
    def next_note_id():
        command = "SELECT note_id FROM notes;"
        info = c.execute(command)

        pre_id = -1
        for ids in info:
            #print(ids)
            pre_id = max(ids or [-1])
        next_id = pre_id + 1

        #print next_id
        return next_id

    #gets the next order id (determines placement of that username's notes)
    def next_order_id():
        command = 'SELECT order_id FROM notes WHERE username="' + username +'";'
        info = c.execute(command)

        pre_id = -1
        for ids in info:
            #print (ids)
            pre_id = max(ids or [-1])
        next_id = pre_id + 1

        #print next_id
        return next_id

    note_id = next_note_id()
    order_id = next_order_id()

    c.execute('INSERT INTO notes VALUES (?,?,?,?,?,?,?,?,?,?,?)',[note_id, username, note_title, note_type, order_id, color, pinned, archived, reminder_time, reminder_repeat, image])

    if note_type == 'notlist':
        #print content
        c.execute('INSERT INTO notlist VALUES (?,?)', [note_id, content])
    else:
        i = 0
        while i < len(content):
            item = content[i]
            checked = checked_items[i]
            #print item
            c.execute('INSERT INTO list VALUES (?,?,?,?)', [note_id, item, i, checked])
            i += 1

    db.commit()
    db.close()

#GET NOTES
#returns a list of dictionaries which contain note_id, note_type, order_id, color, pinned, reminder_time, reminder_repeat, image, and content (the keys are these words).
#if note is a list, content is a list of tuples which contain the list item, the item number (the order in which they are displayed), and checked status (boolean), in that order.

#in between function - do not use in app.py
def get_notes_temp(username, archived):
    f=os.path.dirname(__file__) or '.'    
    f+="/../data/app.db"
    db = sqlite3.connect(f)
    c = db.cursor()

    notes_list = []

    command = 'SELECT note_id, note_title, note_type, order_id, color, pinned, reminder_time, reminder_repeat, image FROM notes WHERE username="' + username +'" AND archived=' + str(archived) + ';'
    info = c.execute(command)

    for note in info:
        #print note
        
        d = {}
        d['note_id'] = note[0]
        d['note_title'] = note[1]
        d['note_type'] =  note[2]
        d['order_id'] = note[3]
        d['color'] = note[4]
        d['pinned'] = (note[5] == 1)
        d['reminder_time'] = note[6] #format: 'YYYYMMDD hh:mm:ss'
        d['reminder_repeat'] = note[7]
        d['image'] = note[8]

        notes_list.append(d)

    for d in notes_list:
        note_id = d['note_id']
        if d['note_type'] == 'list':
            content = []
            
            com = 'SELECT item, item_num, checked FROM list WHERE note_id=' + str(note_id) + ';'
            i = c.execute(com)

            for item_info in i:
                content.append((item_info[0], item_info[1], (item_info[2] == 1)))

        else:
            content = ''
            com = 'SELECT content FROM notlist WHERE note_id=' + str(note_id) + ';'
            i = c.execute(com)
            for stuff in i:
                content = stuff[0]

        #add content to dictionary
        d['content'] = content
    
    return notes_list

#get notes that are NOT archived
def get_nonarch_notes(username):
    return get_notes_temp(username, 0)

#get notes that are archived
def get_arch_notes(username):
    return get_notes_temp(username, 1)

def edit_note_content(note_id, new_content, checks=None):
    f=os.path.dirname(__file__) or '.'
    f+="/../data/app.db"
    db = sqlite3.connect(f)
    c = db.cursor()

    command = 'SELECT note_type FROM notes WHERE note_id=' + str(note_id) + ';'
    info = c.execute(command)

    for types in info:
        note_type = types[0]
    

    if note_type == 'list':
        c.execute('DELETE FROM list WHERE note_id=' + str(note_id) + ';')
        i = 0
        while i < len(new_content):
            new_item = new_content[i]
            if checks == None:
                checked = False
            else:
                checked = checks[i]
            c.execute('INSERT INTO list VALUES (?,?,?,?)', [note_id, new_item, i, checked])
            i += 1

    else:
        c.execute('UPDATE notlist SET content="' + new_content + '" WHERE note_id=' + str(note_id) + ';')

    db.commit()
    db.close()


if __name__ == '__main__':
    #table_creation()
    user = 'testa'
    if not check_username(user):
        add_user('testa', 'hi')

    print check_login('testa', 'hi')
    print check_login('testa', 'no')
    print check_login('hi', 'hi')

    #add_note('testa','hi', 'notlist', 'red', False, False, 'Hi')
    #add_note('testa', 'stuff', 'list', 'white', True, True, ['one', 'two', 'three'],'2018-06-01 12:00:00', 'once', [False, False, False], 'https://testlink.jpg')

    print (get_nonarch_notes('testa'))
    print (get_arch_notes('testa'))

    edit_note_content(0, 'hello')
    edit_note_content(1, ['uno', 'dos', 'tres'])

    print (get_nonarch_notes('testa'))
    print (get_arch_notes('testa'))