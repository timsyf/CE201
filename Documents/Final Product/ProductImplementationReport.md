# Team Implementation Report
*This section should describe the technical details of your implementation.  The subheadings and italicised text below may be used to guide you.*

## Technical Diagrams
*Include a class diagram / circuit diagram, and/or any other relevant technical diagrams.*

## Technical Description
*This section should describe the software implementation in prose form.  Focus on how the code was designed and built.* 
*It should make a clear description that could be used by any future developers to maintain and extend your code, if necessary.*
*Describe important functions / classes / class hierarchies.*
*In this section, you should also wish to highlight any technical achievements your team is particularly proud of, including relevant code snippets.*

## Algorithms and Data Structures
*Describe datastructures of at least one component of your implementation.*
*Describe at least one algorithm used in your implementation.*
*In both cases, describe the space / time complexity of each.*

## Imported Libraries 
*List any 3rd party libraries that were used and describe what functionality they provided.*

## Known Issues
*List any known issues (bugs) in your software, and describe workarounds if they exist.*


Product Implementation Report
Insert the content or screenshot of your team’s ProductImplementationReport.md document here.
# Team Implementation Report
 *This section should describe the technical details of your implementation.  The subheadings and italicised text below may be used to guide you.*


 ## Technical Diagrams
 *Include a class diagram / circuit diagram, and/or any other relevant technical diagrams.



 ## Technical Description
 *This section should describe the software implementation in prose form.  Focus on how the code was designed and built.*
 *It should make a clear description that could be used by any future developers to maintain and extend your code, if necessary.*
 *Describe important functions / classes / class hierarchies.*
 *In this section, you should also wish to highlight any technical achievements your team is particularly proud of, including relevant code snippets.*

 ## Algorithms and Data Structures
 *Describe datastructures of at least one component of your implementation.*
 *Describe at least one algorithm used in your implementation.*
 *In both cases, describe the space / time complexity of each.*

Authentication System
Data Structures
The authentication component relies on the User table in the database. This table has fields for id, name, role, password_hash, and department_id. The structure is essentially a relational table in an SQL database, optimized for efficient data retrieval and integrity.

User Table: Stores user credentials and roles. The password_hash field uses bcrypt for secure password storage. The table is indexed by the id field for fast lookup.
Algorithm
The authentication process consists of two main steps: password verification and session creation.

Password Verification: Upon login attempt, the system retrieves the user's password_hash based on the provided username. It then uses the bcrypt algorithm (via check_password_hash) to verify the submitted password against the stored hash.

Session Creation: If the password verification is successful, a session is created, storing essential user information like user_id, user_role, and department_id for access control throughout the user's session.

Time Complexity: O(1) for password verification due to direct access through the id or username. Bcrypt's time complexity is adjustable and designed to be computationally intensive to resist brute-force attacks.
Space Complexity: Primarily depends on the number of users. Each user's data storage is constant, leading to O(n) space complexity, where n is the number of users.
Department Information Management
Data Structures
This feature utilizes two main tables: Department and DepartmentHR.

Department Table: Stores department details, including id, name, default_total_hours, core_skills_percentage, and soft_skills_percentage. It's structured for straightforward department management.

DepartmentHR Table: Manages the many-to-many relationships between HR officers and departments, indicating which departments each HR officer can manage.

Algorithm
Managing department assignments for HR officers involves inserting or updating records in the DepartmentHR table to reflect the relationships between HR officers and departments.

Assignment Update: The algorithm checks for an existing assignment between an HR officer and a department. If none exists, it creates a new record. If an update is required, it modifies the existing record.

Time Complexity: The operation's time complexity is O(log n) for insertion and searching, assuming the database uses efficient indexing. If no indexing is used, the complexity could degrade to O(n).

Space Complexity: The space complexity is O(m), where m is the number of HR officer and department assignments. Each record's size is constant, but the total space required grows linearly with the number of assignments.


 ## Imported Libraries
 *List any 3rd party libraries that were used and describe what functionality they provided.*
Tailwind, plotly.expressd, openpyxl


 ## Known Issues
 *List any known issues (bugs) in your software, and describe workarounds if they exist.*
  

