import pandas as pd
import xlrd
from app.models import Srep, Leaver, Suspect, Buckets
from app import app, db
import os
import datetime
from flask_login import current_user
import bokeh.plotting
from bokeh.embed import components
from sqlalchemy import func

######## Bokeh ##############
def create_figure(b_selection, bins):
    leavers = Leaver.query.all()
    df = pd.DataFrame([(d.name, d.result, d.id) for d in leavers],
        columns=['name', 'result', 'id'])
    df = df.groupby('result')['name'].count()
    p = Histogram(df, b_selection, title='Leaver Groups', color='Species',
        bins=bins, legend='top_right', width=600, height=400)

        # Set the x axis label
    p.xaxis.axis_label = b_selection

    # Set the y axis label
    p.yaxis.axis_label = 'Count'
    return p


######## Utilities ##############
def result(target, field, rez, flag):
    print('Starting Result Processing...')
    print('Result Content As Delivered: ')
    print(target)
    print(field)
    print(rez)
    print(flag)
    if rez == 'Recapture' or rez == 'Lead' or rez == 'Left Industry':
        target.result = rez
        target.prosrole = target.trackrole
        target.prosfirm = target.trackfirm
        target.outprosshell = datetime.datetime.now(datetime.timezone.utc)
        target.inprosshell = 'No'

    elif rez == 'Inactive':
        target.result = rez

    elif rez == 'Tracking':
        print('Confirmed: ', rez)
        target.link = flag
        target.trackend = None
        target.trackrole = None
        target.trackfirm = None
        target.tracklocation = None
        target.lasttracked = None
        target.outprosshell = datetime.datetime.now(datetime.timezone.utc)
        target.result = rez
        target.inprosshell = 'No'
        target.trackstart = datetime.datetime.now(datetime.timezone.utc)

    db.session.commit()
    print('Result Proces Complete')
    return 'Success'

######## Index/Homepage HELPERS ##############
#populates placed leavers in table on homepage
def proslinkgen(num):
    snum = str(num)
    fnum = snum[:6]
    snum = snum[6:]
    link = 'PROS C ' + fnum + ' ' + snum
    return link

def gen_trackalert_table(trackalert_list):
    ta_headers = str('<thead><tr><th>ID</th>'
                + '<th>Name</th>'
                + '<th>Old Role</th>'
                + '<th>Old Firm</th>'
                + '<th>New Role</th>'
                + '<th>New Firm</th>'
                + '<th>Location</th>'
                + '<th>Link</th>'
                + '<th>Alert Date</th>'
                + '<th>Actions</th>'
                + '</tr></thead><tbody>')
    table_body = ''

    for item in trackalert_list:
        table_body += str('<tr><td>'
        + str(item['leaverid']) + '</td><td>'
        + str(item['leavername']) + '</td><td>'
        + str(item['leaverrole']) + '</td><td>'
        + str(item['leaverfirm']) + '</td><td>'
        + str(item['trackrole']) + '</td><td>'
        + str(item['trackfirm']) + '</td><td>'
        + str(item['leaverlocation']) + '</td><td><a target="_blank" href="'
        + str(item['leaverlink']) + ' ">LinkedIn</a></td><td>"'
        + str(item['trackend']) + ' "</td><td><div class="dropdown"><div class="btn-group">'
        + '<button class="btn btn-primary dropdown-toggle" type="button" id="dropdownMenu" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'
        + 'Action<span class="caret"></span></button>'
        + '<ul class="dropdown-menu" aria-labelledby="dropdownMenu">'
        + '<li><a class="dropdown-item" href="#">Recapture</a></li>'
        + '<li><a class="dropdown-item" href="#">Lead</a></li>'
        + '<li><a class="dropdown-item" href="#">Left Industry</a></li>'
        + '<li><a class="dropdown-item" href="#">Error</a></li></ul></div></div></td></tr>')
    table_body += '</tbody>'
    table = ta_headers + table_body
    return(table)

def gen_dropped_table(drop_list):
    drop_headers = str('<thead><tr>'
                        + '<th>ID</th>'
                        + '<th>Name</th>'
                        + '<th>Role</th>'
                        + '<th>Firm</th>'
                        + '<th>PROS Link</th>'
                        + '<th>Actions</th>'
                        + '</tr></thead><tbody>')
    table_body = ''
    for item in drop_list:
        table_body += str('<tr><td>'
        + str(item['leaverid']) + '</td><td>'
        + str(item['leavername']) + '</td><td>'
        + str(item['prosrole']) + '</td><td>'
        + str(item['prosfirm']) + '</td><td>'
        + str(item['proslink']) + ' </td><td><div class="dropdown"><div class="btn-group">'
        + '<button class="btn btn-primary dropdown-toggle" type="button" id="dropdownMenu" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'
        + 'Action<span class="caret"></span></button>'
        + '<ul class="dropdown-menu" aria-labelledby="dropdownMenu">'
        + '<li><a class="dropdown-item" href="#">Recapture</a></li>'
        + '<li><a class="dropdown-item" href="#">Lead</a></li>'
        + '<li><a class="dropdown-item" href="#">Left Industry</a></li>'
        + '<li><a class="dropdown-item" href="#">Manual Track</a></li>'
        + '<li><a class="dropdown-item" href="#">Inactive</a></li></ul></div></div></td></tr>')
    table_body += '</tbody>'
    table = drop_headers + table_body
    return(table)

def actionfill(flag):
    parentdict = {}
    DROP_dict = {}
    DROP_list = []
    TA_dict = {}
    TA_list = []
    if flag == 'B':
        print('Flag is B')
        TA_Confirm = Leaver.query.filter_by(result='TrackAlert', repcode=current_user.repcode).all()
        for l in TA_Confirm:
            TA_dict = {'leavername': l.name, 'leaverfirm': l.leaverfirm, 'leaverrole': l.leaverrole, 'leaverid': l.id, 'trackend': l.trackend, 'leaverlocation': l.leaverlocation, 'leaverlink': l.link, 'trackfirm': l.trackfirm, 'trackrole': l.trackrole}
            TA_list.append(TA_dict)
        ta_table = gen_trackalert_table(TA_list)
        parentdict['B'] = ta_table

    elif flag == 'A':
        print('Flag is A')
        DROP_Confirm = Leaver.query.filter_by(inprosshell='No', result='Lost', repcode=current_user.repcode).all()
        for d in DROP_Confirm:
            # num = d.prosnum
            # link = proslinkgen(num)
            DROP_dict = {'leavername': d.name, 'prosfirm': d.prosfirm, 'prosrole': d.prosrole, 'leaverid': d.id, 'proslink': proslinkgen(d.prosnum)}
            DROP_list.append(DROP_dict)
        dropped_table = gen_dropped_table(DROP_list)
        parentdict['A'] = dropped_table

    elif flag == 'AB':
        print('Flag is AB')
        TA_Confirm = Leaver.query.filter_by(result='TrackAlert', repcode=current_user.repcode).all()
        DROP_Confirm = Leaver.query.filter_by(inprosshell='No', result='Lost', repcode=current_user.repcode).all()

        for l in TA_Confirm:
            TA_dict = {'leavername': l.name, 'leaverfirm': l.leaverfirm, 'leaverrole': l.leaverrole, 'leaverid': l.id, 'trackend': l.trackend, 'leaverlocation': l.leaverlocation, 'leaverlink': l.link, 'trackfirm': l.trackfirm, 'trackrole': l.trackrole}
            TA_list.append(TA_dict)
        ta_table = gen_trackalert_table(TA_list)
        parentdict['B'] = ta_table
        for d in DROP_Confirm:
            # num = d.prosnum
            # link = proslinkgen(num)
            DROP_dict = {'leavername': d.name, 'prosfirm': d.prosfirm, 'prosrole': d.prosrole, 'leaverid': d.id, 'proslink': proslinkgen(d.prosnum)}
            DROP_list.append(DROP_dict)
        dropped_table = gen_dropped_table(DROP_list)
        parentdict['A'] = dropped_table

    return parentdict

def dropfill():
    dropped = Leaver.query.filter_by(inprosshell='No', result='Lost', repcode=current_user.repcode).all()
    parentdict = {}
    placed_dict = {}
    placed_list = []
    for l in dropped:
        num = l.prosnum
        link = proslinkgen(num)
        placed_dict = {'leavername': l.name, 'prosfirm': l.prosfirm, 'prosrole': l.prosrole, 'leaverid': l.id, 'proslink': link}
        placed_list.append(placed_dict)
    parentdict['B'] = placed_list
    return parentdict

def reset_leaver(id):
    lvr_id = int(id)
    reset_lvr = Leaver.query.filter_by(id=lvr_id).first()
    reset_suspects = Suspect.query.filter_by(leaverid=lvr_id).all()
    reset_lvr.result = 'Tracking'
    #reset_lvr.leaverrole = None
    #reset_lvr.leaverfirm = None
    #reset_lvr.leaverlocation = None
    #reset_lvr.link = None
    reset_lvr.trackrole = None
    reset_lvr.trackfirm = None
    reset_lvr.tracklocation = None
    reset_lvr.lasttracked = None
    reset_lvr.datetimeresult = None
    #reset_lvr.suspectcheck = None
    reset_lvr.trackend = None
    #for s in reset_suspects:
        #s.datetimeresult = None
        #s.result = None
    db.session.commit()
    return 'Success'

######## UPLOAD HELPERS ##############
#sets the inpros flag in db to NO to detect those No longer in the LJFT bucket
def inpros():
    existnames = Leaver.query.filter_by(result='Lost').all()
    for n in existnames:
        n.inprosshell = 'No'
    return 'Success'

#adds pros shell and pros contact numbers together
def concat(a, b):
    return int(f"{a}{b}")

#translates excel file to pandas df passing rows to pd2class
def processfile(file):
    data_xls = pd.read_excel(file)
    try:
        data_xls["name"] = data_xls["first"] + ' ' + data_xls["last"]
        data_xls = data_xls.drop('first', 1)
        data_xls= data_xls.drop('last', 1)
        data_xls.fillna(' ', inplace=True)
        data_xls.apply(pd2class, axis=1)
        return 'Success'
    except:
        print('Failed to Read SpreadSheet. Please Check Columns')
        return 'Failure'

#adds NEW leavers to database from pandas df
def pd2class(row):
    number = concat(row['prosshell#'], row['proscontact#'])
    number = int(number)
    exists = Leaver.query.filter_by(prosnum=number).first()
    if exists:
        exists.inprosshell = 'Yes'
        print('duplicate detected. Skipping: ', row['name'])
        db.session.commit()
    else:
        l = Leaver(prosnum=number, name=row['name'], repcode=row['repcode'], teamcode=row['teamcode'], prosfirm=row['firm'], prosrole=row['role'], inprosshell='Yes')
        print('Adding Leaver to DB: ', l.name)
        db.session.add(l)
        db.session.commit()

def exitpros():
    newdrop = Leaver.query.filter_by(inprosshell='No').all()
    for n in newdrop:
        if n.outprosshell == None:
            n.outprosshell = datetime.datetime.now(datetime.timezone.utc)
    db.session.commit()
    return 'Success'
####### Match HELPERS ############
#populates the dropdown on track page with leavers. selection triggers tablefill
def fillselect(leavers):
    leaver_dict = []

    for l in leavers:
        suspects = Suspect.query.filter_by(leaverid=l.id, result=None).all()
        num = len(suspects)
        if num > 0:
            dval = l.name + ' ' + '(' + str(num) + ')'
            s_dict = {'ident': l.id, 'name': dval}
            leaver_dict.append(s_dict)
    return leaver_dict


#populates dictionary for suspect table on fillselect selection AND comparison card
def populate_table(thing):
    l = Leaver.query.filter_by(id=thing).first()
    ddate = l.datetimeadded.date().strftime('%m/%d/%Y')
    parentdict = {}
    susp_list = []
    leaverdict = {'leavername': l.name, 'leaverfirm': l.prosfirm, 'leaverrole': l.prosrole, 'leavertime': ddate}
    suspects = Suspect.query.filter_by(leaverid=thing, result=None).all()
    for s in suspects:
        s_dict = {'ident': s.id, 'name': s.name, 'link': s.slink, 'role': s.srole, 'firm':s.sfirm, 'location': s.slocation}
        susp_list.append(s_dict)
    parentdict['A'] = leaverdict
    parentdict['B'] = susp_list
    return parentdict

def chart_data(type):
    data = {}
    if type == 'doughnut':
        print('getting data for doughnut chart')
        result_list = []
        count_list = []
        for result, count in db.session.query(Leaver.result, func.count(Leaver.id)).group_by(Leaver.result).all():
            print('Users status %s: %d' % (result, count))
            result_list.append(result)
            count_list.append(count)
        data['labels'] = result_list
        data['datasets'] = count_list
        return data
    elif type == 'stackedbar':
        print('getting data for bar chart')
        data = {}
        df = pd.read_sql(db.session.query(Buckets).statement,db.session.bind)
        df.date = df.date.apply(lambda x: str(x).split(' ')[0])
        dates = df.date.unique()
        dt_list = []
        for d in dates:
            dt_list.append(d)
        data['labels'] = dt_list

        label_list = []
        for l in df.status.unique():
            label_list.append(l)
        list_data = []
        for l in label_list:
            d = {}
            members = db.session.query(Buckets).filter_by(status=l).all()
            values = []
            for m in members:
                values.append(m.count)
            d['set'] = [m.status, values]
            list_data.append(d)

        data['datasets'] = []
        for i in list_data:
            j = {}
            j['label'] = i['set'][0]
            j['data'] = i['set'][1]
            data['datasets'].append(j)

        colors = ["#c45850", "#e8c3b9", "#3cba9f", "#8e5ea2", "#3e95cd", "#3e95cd", "#5e4fa2", '#D6E9C6']
        i = 0
        while i < len(data['datasets']):
            data['datasets'][i]['backgroundColor'] = colors[i]
            i += 1

        return data

    # else:
    #     data = {}
    #     dough = {}
    #     result_list = []
    #     count_list = []
    #     for result, count in db.session.query(Leaver.result, func.count(Leaver.id)).group_by(Leaver.result).all():
    #         print('Users status %s: %d' % (result, count))
    #         result_list.append(result)
    #         count_list.append(count)
    #     dough['labels'] = result_list
    #     dough['datasets'] = count_list
    #
    #     bar = {}
    #     df = pd.read_sql(db.session.query(Buckets).statement,db.session.bind)
    #     df.date = df.date.apply(lambda x: str(x).split(' ')[0])
    #     df1 = df.groupby("date").count()
    #     dfgroup = df1.reset_index()
    #     lst = list(dfgroup.date)
    #     date_list = lst
    #     bar['labels'] = date_list
    #     datasets = []
    #     labels = ['Tracking', "Lost", "Inactive", "Recapture", "Lead", "TrackAlert"]
    #     for l in labels:
    #         dset = {}
    #         members = db.session.query(Buckets).filter_by(status=l).all()
    #         values = []
    #         for m in members:
    #             values.append(m.count)
    #         dset[l] = values
    #         datasets.append(dset)
    #     bar['datasets'] = datasets
    #
    #     data['dough'] = dough
    #     data['bar'] = bar
    #     return data
