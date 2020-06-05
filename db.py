import sqlite3
import time
from error_codes import SUCCESS, MISSING_ID, DUPLICATE_SUBMISSION, FATAL_ERROR


class AttendanceFormDB:

    def __init__(self):
        # create connection
        self.connection = sqlite3.connect('databases/attendance_form.db')
        # get the cursor
        self.cursor = self.connection.cursor()
        # get the current date and time
        self.current_date_time = time.localtime()
        # generate the table name
        self.table_name = 'attendance_' + self.get_date()

    def create_table(self):
        """
        Creates a table with a specified name
        """
        # format of table name is attendance_year_month_day
        query = '''CREATE TABLE IF NOT EXISTS ''' + self.table_name + ''' (
                    "COUNT"	INTEGER NOT NULL,
                    "ID"	TEXT NOT NULL,
                    "NAME"	TEXT NOT NULL,
                    "COURSE"	TEXT NOT NULL,
                    "PHONE"	TEXT NOT NULL,
                    "SUBMISSION_TIME"	TEXT NOT NULL,
                    PRIMARY KEY("COUNT" AUTOINCREMENT)
                );'''
        self.cursor.execute(query)
        # save the changes
        self.connection.commit()

    def submit_data(self, stud_id, name, course, phone, operation_type):
        """
        Inserts or edits data as appropriate
        """
        if operation_type == 'insert':
            return self.insert_data(stud_id, name, course, phone)
        if operation_type == 'edit':
            return self.edit_data(stud_id, name, course, phone)

    def insert_data(self, stud_id, name, course, phone):
        """
        Inserts the data into the attendance table
        """
        try:
            # get the course code
            course_code = self.get_course_code(course)
            # create the table if it does not exist
            self.create_table()
            # check if the ID exists before updating
            query = "SELECT COUNT(ID) FROM " + self.table_name + \
                " WHERE ID='" + stud_id + "' AND COURSE LIKE '" + course_code + "%';"
            result = self.cursor.execute(query)
            data = result.fetchone()
            if data[0] != 0:
                return DUPLICATE_SUBMISSION
            # get the current time and use it as submission time
            submission_time = self.get_time()
            # submit the data
            query = "INSERT INTO " + self.table_name + \
                "(ID, NAME, COURSE, PHONE, SUBMISSION_TIME) VALUES(?,?,?,?,?);"
            self.cursor.execute(
                query, (stud_id, name, course, phone, submission_time))
            # save the changes
            self.connection.commit()
            return SUCCESS
        except:
            return FATAL_ERROR

    def edit_data(self, stud_id, name, course, phone):
        """
        Edits the data in the attendance table
        """
        try:
            # get the course code
            course_code = self.get_course_code(course)
            # check if the ID exists before updating
            query = 'SELECT COUNT(ID) FROM ' + self.table_name + \
                " WHERE ID='" + stud_id + "' AND COURSE LIKE '" + course_code + "%';"
            result = self.cursor.execute(query)
            data = result.fetchone()
            if data[0] == 0:
                return MISSING_ID
            # get the current time and use it as submission time
            submission_time = self.get_time()
            # update the data
            query = "UPDATE " + self.table_name + \
                " SET NAME=?, COURSE=?, PHONE=?, SUBMISSION_TIME=? WHERE ID='" + \
                    stud_id + "' AND COURSE LIKE '" + course_code + "%';"
            self.cursor.execute(query, (name, course, phone, submission_time))
            # save the changes
            self.connection.commit()
            return SUCCESS
        except:
            return FATAL_ERROR

    def get_table_data(self):
        """
        Gets all the table data
        """
        # select all data
        query = 'SELECT * FROM ' + self.table_name + " ORDER BY COUNT DESC;"
        result = self.cursor.execute(query)
        data = result.fetchall()
        # return the data
        return data

    def close_connection(self):
        """
        Closes the database connection
        """
        self.connection.close()

    def get_time(self):
        """
        Returns the time 
        """
        return ':'.join([self.get_padded_value(self.current_date_time.tm_hour),
                         self.get_padded_value(self.current_date_time.tm_min),
                         self.get_padded_value(self.current_date_time.tm_sec)])

    def get_padded_value(self, value):
        """
        Pads values with zeros to get length of 2
        """
        value = str(value)
        return "0" + value if len(value) == 1 else value

    def get_date(self):
        """
        Returns the date for creating the table
        """
        return '_'.join([str(self.current_date_time.tm_year),
                         str(self.current_date_time.tm_mon),
                         str(self.current_date_time.tm_mday)])

    def get_course_code(self, course):
        """
        Extract the course code from the course name
        """
        return course.split('-')[0].strip()
