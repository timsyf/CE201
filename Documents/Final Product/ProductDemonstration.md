# Product Demonstration Report

*This section should contain a brief description and demo of product you have built.*

* *Include screenshots (actual screenshots, not mock ups) of all of the facets of the product working.*
* *Link consecutive screenshots together with a brief narrative explaining how the product works, e.g. a sentence "Click on OK and it takes you to the next window", "On starting the app, the following window is shown".  This document should not take you a long time to create - it's just pasting photos and adding explanatory sentences between them, so that your MVP is adequately described.*
* *Make sure an image of each window of your software is included - so that a person who has not seen the actual demo of the product has a good idea of what your product currently does.*
* *If your product is a physical device (a hardware product) then you may replace all of the above screenshots by actual photos/vidoes where you feel it is appropriate.*
* *Make sure this section includes any functionality/features you are particularly proud of.*
* *Indicate clearly which parts of the functionality shown in the screenshots are currently incomplete, and what is likely to change in the final version.  For example if a graph displayed is currently based on static hard-coded data for the MVP, but in the future version the graph will dynamically change depending on fresh data, then point this out explicitly.*

Document URL:  Include a gitlab URL to the working version of this Word document.
Final Product Demonstration
SIGN UP

Sign up page for users to sign up, users need to input their username, password and role to sign up. 

There are two checks:
-If either one or both username and password are empty, it will show an error message.
-if the username that the user wants to use exists, the user will need to change the username

Registration successful message will show and bring the user to the Sign in page after signing up.
SIGN IN

There are two checks for a user to sign in:
-Does user exist
-Is the password correct

It will show an error message if one of the checks fails.


DASHBOARD SECTION

After logging in with any user account and role, you'll find yourself on the dashboard automatically. If not, simply click the "Dashboard" link in the sidebar to navigate there.


The dashboard provides a summary of the latest courses from the past week, month, and year.


The dashboard displays a summary of courses that the current user has applied for, showing the total duration, name, and type of each course.
PROFILE SECTION

After logging in with user role Staff/HR officers/HR supervisors, navigate to the sidebar and click on the "Profile" link.

When Staff click on ‘Profile’, the staff can see:
-username
- role 
-department
-Change Username button
-Change Password button
-HR officers in Department 
-Staff in Department

When HR officer click on ‘Profile’ the HR officer can see:
-username
-role
-Change Username button
-Change Password button
-Assigned Departments 

When HR supervisor click on ‘Profile’ the HR supervisor can see:
-username
-role
-Change Username button
-Change Password button

When users click on ‘Change Username’ button in ‘Profile’, they can input the new username they want.
There’s a check to see whether is the new username taken. Users can click on ‘Cancel’ button if they want to go back to ‘Profile’
A success message will show after username has been changed. 

When users click on ‘Change Password’ button in ‘Profile’, they need to input:
-Current Password
-New Password
-Confirm New Password
.
There are checks to make sure the new password is valid:
-check current password is correct
-check the new password and confirm new password match
If any checks failed, it will show error message. Users can click on ‘Cancel’ button if they want to go back to ‘Profile’
A success message will show after password has been changed. 
DEPARTMENTS SECTION

After logging in with a HR officer or HR supervisor account navigate to the sidebar and click on the "Departments" link.

HR supervisor will see 
-Add Department button
-Department Name
-Total Training Hours
-Core Skills (%)
-Soft Skills (%)
-Staff in Deprtment
-HR Officers assigned
-Actions with Edit and Delete buttons

HR officers will see


-Add Department button
(departments that assigned to them only)
-Department Name
-Total Training Hours
-Core Skills (%)
-Soft Skills (%)
-Staff in Deprtment
-Actions with Edit and Delete buttons

When HR officers or HR supervisors click on the staff count(blue and underline) in th Staff in Department column, they will be able to see the Staff details page for that Department.


In this page, they can add Staff or remove Staff to that Department.

One staff can only be added to one department 




HR officer and HR supervisor can also click the username of the staff(blue and underline)  in the department when they are in the staff details page.

they will then go in this individual Staff Training Requirement, here they can adjust the training requirements for that individual staff.




When HR officers or HR supervisors click on ‘Add Department” in the Departments page, it will bring them to ‘Add Department’ page where they can add a new Department, they can also adjust the new departments requirements in this page.

HR officers can only edit department, not delete department 

HR officers and HR supervisors can edit department detail and requirements when they click the ‘Edit’ button in the Department page.

HR HR supervisors will need to remove all staff and unassigned all HR officers in order to delete the department.




When HR supervisor click in the HR officers’ count (blue and underline) in the ‘HR Officers Assigned’ column in the department page, it will bring HR supervisor to this page where HR supervisor can assign and unassign HR officers to the department.

One HR officer can be assigned to multiple departments.
REPORT SECTION

After logging in with a user account that has the officer role, navigate to the sidebar and click on the "Reports" link.

You'll encounter a dropdown menu where you can select the specific report you wish to download.

Selecting the first option leads you to the staff information report, offering a detailed overview of everything related to a selected staff member.







Once you click on "Export Data," an Excel sheet containing the staff information will be downloaded.

Choosing the second option directs you to the Department Information section, where you can access details about departments created in any given year.



Upon clicking "Export Data," an Excel sheet containing the department information will be downloaded.

Selecting the third option takes you to the Department Completion Information Report, providing a comprehensive view of everything related to a selected department.



Upon clicking "Export Data," an Excel sheet containing the department completion information report will be downloaded.
COURSES SECTION

Add course page for only accessible by supervisor to add courses.

List of courses page. The Update and delete button is only visible to Supervisors.

Update course page, only available to supervisor to edit course details

Delete course prompt, when clicked on delete course a message will prompt user to confirm before deleting the selected course

List of course page viewed by staff, the “Apply” button is available for staffs to apply for courses

Staffs are able to select multiple or single date from the available dates within the selected course when applying for the course

Staffs are able to view the applied course and the selected start date.

They are also able to delete the applied course.
Attendance Section

Users with instructor role is able to access the attendance taking page. 

List of courses that had been applied will be shown and instructors is able to mark the attendance for the staff

When instructor has marked the attendance, staff can view their attended courses in the attended courses page



