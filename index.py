from flask import Flask, render_template, url_for, request, redirect
from db import AttendanceFormDB
from error_codes import SUCCESS, MISSING_ID, DUPLICATE_SUBMISSION, FATAL_ERROR

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # initialize the error message
        error_msg = 'Submission failed: '
        # get the form data
        course = str(request.form['courses'])
        name = str(request.form['name'])
        stud_id = str(request.form['id'])
        phone = str(request.form['phone'])
        operation_type = str(request.form['operationType'])
        # submit to database
        try:
            db_class = AttendanceFormDB()
            return_code = db_class.submit_data(stud_id, name, course,
                                               phone, operation_type)
            db_class.close_connection()
        except:
            # generate error message
            error_msg += 'fatal error!'
            # show error message
            return redirect(url_for('failure', error_msg=error_msg))
        # return codes
        # 0 = success, -1 = duplicate submission, 1 = editing unsubmitted ID
        if return_code == SUCCESS:
            # show success page
            success_msg = 'Attendance ' + \
                ('submitted' if operation_type ==
                    'insert' else 'edited') + ' successfully!'
            return redirect(url_for('success', success_msg=success_msg))
        elif return_code == DUPLICATE_SUBMISSION:
            # generate error message
            error_msg += stud_id + ' has already been submitted!'
        elif return_code == MISSING_ID:
            # generate error message
            error_msg += stud_id + ' has not been submitted!'
        else:
            # generate error message
            error_msg += 'fatal error!'
        # show error message
        return redirect(url_for('failure', error_msg=error_msg))


@app.route('/success/<success_msg>')
def success(success_msg):
    """
    Show success page
    """
    try:
        db_class = AttendanceFormDB()
        data = db_class.get_table_data()
        db_class.close_connection()
        return render_template('success.html', success_msg=dict(msg=success_msg, data=data))
    except Exception as e:
        error_msg = 'Fatal error:' + str(e)
        return render_template('failure.html', error_msg=dict(msg=error_msg, data=[]))


@app.route('/failure/<error_msg>')
def failure(error_msg):
    """
    Show success page
    """
    try:
        db_class = AttendanceFormDB()
        data = db_class.get_table_data()
        db_class.close_connection()
        return render_template('failure.html', error_msg=dict(msg=error_msg, data=data))
    except Exception as e:
        error_msg = 'Fatal error:' + str(e)
        return render_template('failure.html', error_msg=dict(msg=error_msg, data=[]))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
