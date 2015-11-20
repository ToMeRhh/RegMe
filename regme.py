# -*- coding: cp1255 -*-
def logout(row_id, cookie):
    data = {'rc_rowid':row_id}
    req = requests.post("https://bgu4u.bgu.ac.il/pls/scwp/!SC.BYEBYEHD",
                        headers=create_headers("https://bgu4u.bgu.ac.il/pls/scwp/!sc.AddCourse", cookie),
                        data=data)
    print req
    write_to_file("logoutfinish.html", req.content)



def regme(regdata, cookie):
    req = requests.post("https://bgu4u.bgu.ac.il/pls/scwp/!sc.AddCourse",
                        headers=create_headers("https://bgu4u.bgu.ac.il/pls/scwp/!sc.CourseConsult", cookie),
                        data=regdata)
    print req
    write_to_file("finish.html", req.content)


def create_course_data(items, row_id):
    data = { 'rc_rowid' : row_id }
    for item in items:
        data[item[0]] = item[1]
    return data


def read_from_file(filename):
    f = open(filename, "r")
    line = f.readline()
    f.close()
    return line


def write_to_file(filename, data):
    f = open(filename, "w")
    f.write(data)
    f.close()


def get_rowid(user, password, id_number, cookie):
    auth = {'oc_username' : user, 'oc_password' : password, 'rc_id' : id_number, 'rc_system' : 'sc'}
    req = requests.post("https://bgu4u.bgu.ac.il/pls/scwp/!fw.CheckId", headers=create_headers("https://bgu4u.bgu.ac.il/html/loginsc.php", cookie), data=auth)

    # check for a cookie update: (mostly it WILL happen...)
   # newcookie = ""
   # if 'Set-Cookie' in req.headers:
    #    newcookie = req.headers['Set-Cookie']

    write_to_file('a.html', req.content)

    row_id = ""
    if 'rc_rowid' in req.content:
        row_id = req.content[req.content.index('rc_rowid'):]
        row_id = row_id[row_id.index('value')+7:]
        row_id = row_id[:row_id.index('"')]
        
    if "ברשומותינו" in req.content:
        print "ERROR!!!!!!"

    return row_id    


def get_cookie():
    req = requests.get("https://bgu4u.bgu.ac.il/html/cons.php", headers=create_headers("https://bgu4u.bgu.ac.il/html/loginsc.php"))  # try with another referrer? 
    if 'Set-Cookie' in req.headers:
       return req.headers['Set-Cookie']
    return ""


def create_headers(ref, cookie=""):
    return {'Host' : 'bgu4u.bgu.ac.il',
            'Connection' : 'keep-alive',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Origin' : 'https://bgu4u.bgu.ac.il',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36',
            'Content-Type' : 'application/x-www-form-urlencoded',
            'Referer' : ref,
            'Cookie' : cookie,
            'Accept-Encoding' : 'gzip, deflate',
            'Accept-Language' : 'en-US,en;q=0.8,he;q=0.6'}


def pr_phase(p):
    print """
**************************
{0}
**************************""".format(p)

        
def print_banner():
    print """
#####################################################

REG-ME

This is a simple registration program made by me.
don't use it.
#####################################################
"""


if __name__ == '__main__':
    import argparse
    import sys
    import requests
    import ConfigParser

    sys.argv = ["RegMe.py", "-r", "1"]

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--bgu-username', dest='user', default='*******')
    parser.add_argument('-p', '--bgu-password', dest='password', default='*******')
    parser.add_argument('-i', '--id-number', dest='id', default="201593985")
    parser.add_argument('-y', '--year', dest='year', default="2016")
    parser.add_argument('-s', '--semester', dest='semester', default="1")
    parser.add_argument('-r', '--get-rowid', dest='get-rowid', default=0)
    args = vars(parser.parse_args())


    print_banner()
    print "Using Settings:"
    for i in args.keys():
        print "{0} = {1}".format(i, args[i])

    #get cookie
    pr_phase("Getting cookie...")
    cookie = get_cookie()
    if cookie=="":
        print "Error getting cookie. Aborting."
        sys.exit(-1)
    print "Got cookie:\n {0}".format(cookie)


    #get-row-id mode:
    if args['get-rowid']!=0:
        pr_phase("Logging in to get a unique RowID...")
        row_id = get_rowid(args['user'], args['password'], args['id'], cookie)
        if row_id=="":
            print "Error getting RowID. Aborting."
            sys.exit(-1)
        print "Got RowID:\n {0}".format(row_id)
        write_to_file('row_id.txt', row_id)
        sys.exit(1)



    #load row-id from file:
    pr_phase("Loading RowID from the configuration file...")
    try:
        row_id = read_from_file('row_id.txt')
    except IOError:
        print "Error opening configuration file, use the -r arg first. Aborting."
        sys.exit(-1)

    if row_id == "":
        print "Error getting RowID from configuration file, use the -r arg first. Aborting."
        sys.exit(-1)
        
    print "Loaded RowID:\n {0}".format(row_id)

    print """
    config = ConfigParser.ConfigParser()
    config.readfp(open("courses.txt"))
    
    for sec in config.sections():
        pr_phase("Sending registration request to: {0} , check 'finish.html' for more information.".format(sec))
        course = create_course_data(config.items(sec), row_id)
        regme(course, cookie)        
     """   


    pr_phase("Logging out...")
    logout(row_id, cookie)
    print "Finished. Bye!"
    sys.exit(1)



