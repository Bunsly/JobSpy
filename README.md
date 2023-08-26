# JobSpy AIO Scraper

## Features

- Scrapes job postings from **LinkedIn**, **Indeed** & **ZipRecruiter** simultaneously
- Returns jobs with title, location, company, description & other data
- Optional JWT authorization


### API

POST `/api/v1/jobs/`
### Request Schema


#### Parameters:
```plaintext
Request
├── Required
│   ├── site_type (List[enum]): linkedin, zip_recruiter, indeed
│   └── search_term (str)
└── Optional
    ├── location (int)
    ├── distance (int)
    ├── job_type (enum): fulltime, parttime, internship, contract
    ├── is_remote (bool)
    ├── results_wanted (int): per site_type
    └── easy_apply (bool): only for linkedIn
```

#### Example
<pre>
{
    "site_type": ["linkedin", "indeed"],
    "search_term": "software engineer",
    "location": "austin, tx",
    "distance": 10,
    "job_type": "fulltime",
    "results_wanted": 20
}
</pre>

## Response Schema
### Fields
```plaintext
site_type (enum)
└── response (SiteResponse)
    ├── success (bool)
    ├── error (str)
    ├── jobs (list[JobPost])
    │   └── JobPost
    │       ├── title (str)
    │       ├── company_name (str)
    │       ├── job_url (str)
    │       ├── location (object)
    │       │   ├── country (str)
    │       │   ├── city (str)
    │       │   ├── state (str)
    │       │   ├── postal_code (str)
    │       │   └── address (str)
    │       ├── description (str)
    │       ├── job_type (enum)
    │       ├── compensation (object)
    │       │   ├── interval (CompensationInterval): yearly, monthly, weekly, daily, hourly
    │       │   ├── min_amount (float)
    │       │   ├── max_amount (float)
    │       │   └── currency (str): Default is "US"
    │       └── date_posted (datetime)
    ├── total_results (int)
    └── returned_results (int)
```

### Example
<details>
  <summary>Sample Response JSON</summary>
<pre><code>{
    "linkedin": {
        "success": true,
        "error": null,
        "jobs": [
            {
                "title": "Software Engineer 1",
                "company_name": "Public Partnerships | PPL",
                "job_url": "https://www.linkedin.com/jobs/view/3690013792",
                "location": {
                    "country": "US",
                    "city": "Austin",
                    "state": "TX",
                    "postal_code": null,
                    "address": null
                },
                "description": "Public Partnerships LLC supports individuals with disabilities or chronic illnesses and aging adults, to remain in their homes and communities and “self” direct their own long-term home care. Our role as the nation’s largest and most experienced Financial Management Service provider is to assist those eligible Medicaid recipients to choose and pay for their own support workers and services within their state-approved personalized budget. We are appointed by states and managed healthcare organizations to better serve more of their residents and members requiring long-term care and ensure the efficient use of taxpayer funded services.Our culture attracts and rewards people who are results-oriented and strive to exceed customer expectations. We desire motivated candidates who are excited to join our fast-paced, entrepreneurial environment, and who want to make a difference in helping transform the lives of the consumers we serve. (learn more at www.publicpartnerships.com )Duties & Responsibilities Plans, develops, tests, documents, and implements software according to specifications and industrybest practices. Converts functional specifications into technical specifications suitable for code development. Works with Delivery Manager to evaluate user’s requests for new or modified computer programs todetermine feasibility, cost and time required, compatibility with current system, and computercapabilities. Follows coding and documentation standards. Participate in code review process. Collaborates with End Users to troubleshoot IT questions and generate reports. Analyzes, reviews, and alters program to increase operating efficiency or adapt to new requirementsRequired Skills System/application design, web, and client-server technology. Excellent communication skills and experience working with non-technical staff to understandrequirements necessary.QualificationsEducation & Experience:Relevant Bachelor’s degree required with a computer science, software engineering or information systems major preferred.0-2 years of relevant experience preferred. Demonstrated experience in Microsoft SQL server, Experience working with .NET Technologies and/or object-oriented programming languages. Working knowledge of object-oriented languageCompensation & Benefits401k Retirement PlanMedical, Dental and Vision insurance on first day of employmentGenerous Paid Time OffTuition & Continuing Education Assistance ProgramEmployee Assistance Program and more!The base pay for this role is between $85,000 to $95,000; base pay may vary depending on skills, experience, job-related knowledge, and location. Certain positions may also be eligible for a performance-based incentive as part of total compensation.Public Partnerships is an Equal Opportunity Employer dedicated to celebrating diversity and intentionally creating a culture of inclusion. We believe that we work best when our employees feel empowered and accepted, and that starts by honoring each of our unique life experiences. At PPL, all aspects of employment regarding recruitment, hiring, training, promotion, compensation, benefits, transfers, layoffs, return from layoff, company-sponsored training, education, and social and recreational programs are based on merit, business needs, job requirements, and individual qualifications. We do not discriminate on the basis of race, color, religion or belief, national, social, or ethnic origin, sex, gender identity and/or expression, age, physical, mental, or sensory disability, sexual orientation, marital, civil union, or domestic partnership status, past or present military service, citizenship status, family medical history or genetic information, family or parental status, or any other status protected under federal, state, or local law. PPL will not tolerate discrimination or harassment based on any of these characteristics.PPL does not discriminate based on race, color, religion, or belief, national, social, or ethnic origin, sex, gender identity and/or expression, age, physical, mental, or sensory disability, sexual orientation, marital, civil union, or domestic partnership status, protected veteran status, citizenship status, family medical history or genetic information, family or parental status, or any other status protected under federal, state, or local law.",
                "job_type": null,
                "compensation": null,
                "date_posted": "2023-07-31T00:00:00"
            },
            {
                "title": "Front End Developer",
                "company_name": "Payment Approved",
                "job_url": "https://www.linkedin.com/jobs/view/3667178581",
                "location": {
                    "country": "US",
                    "city": "Austin",
                    "state": "TX",
                    "postal_code": null,
                    "address": null
                },
                "description": "Front-End Developer Austin, TX Who We Are:At Payment Approved, we believe that the key to global money movement is a trusted network that emphasizes safety, security, cost-effectiveness, and accessibility. Our mission is to build the most trusted, comprehensive money movement network for every country, and human, in the world.We bridge the technology gap through financial tools that help businesses access an end-to-end solution for faster, simpler, and more secure payments and money movement around the world.The team at Payment Approved has decades of experience across technology, compliance, and financial services. We are financial and digitization leaders, working together to build an end-to-end solution for simple, secure, and safe money movement around the world.What You’ll Do:Be responsible for building out the Payment Approved Business Portal, our web application that allows our customers to onboard onto our services and products, and to review all of the payment transactions they execute with Payment ApprovedWork within a cross-functional scrum team focused on a given set of features and services in a fast-paced agile environmentCare deeply about code craftsmanship and qualityBring enthusiasm for using the best practices of scalability, accessibility, maintenance, observability, automation testing strategies, and documentation into everyday developmentAs a team player, collaborate effectively with other engineers, product managers, user experience designers, architects, and quality engineers across teams in translating product requirements into excellent technical solutions to delight our customersWhat You’ll Bring:Bachelor’s degree in Engineering or a related field3+ years of experience as a Front-End Developer, prior experience working on small business tools, payments or financial services is a plus2+ years of Vue.js and Typescript experience HTML5, CSS3, JavaScript (with knowledge of ES6), JSON, RESTFUL APIs, GIT, and NodeJS experience is a plusAdvanced organizational, collaborative, inter-personal, written and verbal communication skillsMust be team-oriented with an ability to work independently in a collaborative and fast-paced environmentWhat We Offer:Opportunity to join an innovative company in the FinTech space Work with a world-class team to develop industry-leading processes and solutions Competitive payFlexible PTOMedical, Dental, Vision benefitsPaid HolidaysCompany-sponsored eventsOpportunities to advance in a growing companyAs a firm, we are young, but mighty. We’re a certified VISA Direct FinTech, Approved Fast Track Program participant. We’re the winner of the IMTC 2020 RemTECH Awards. We’re PCI and SOC-2 certified. We operate in 15 countries. Our technology is cutting-edge, and our amazing team is what makes the difference between good and great. We’ve done a lot in the six years we’ve been around, and this is only the beginning.As for 2021, we have our eyes fixed: The money movement space is moving full speed ahead. We aim to help every company, in every country, keep up with its pace. Come join us in this objective!Powered by JazzHROPniae0WXR",
                "job_type": null,
                "compensation": null,
                "date_posted": "2023-06-22T00:00:00"
            },
            {
                "title": "Full Stack Software Engineer",
                "company_name": "The Boring Company",
                "job_url": "https://www.linkedin.com/jobs/view/3601460527",
                "location": {
                    "country": "US",
                    "city": "Austin",
                    "state": "TX",
                    "postal_code": null,
                    "address": null
                },
                "description": "The Boring Company was founded to solve the problem of soul-destroying traffic by creating an underground network of tunnels. Today, we are creating the technology to increase tunneling speed and decrease costs by a factor of 10 or more with the ultimate goal of making Hyperloop adoption viable and enabling rapid transit across densely populated regions.As a Full-Stack Software Engineer you will be responsible for helping build automation and application software for the next generation of tunnel boring machines (TBM), used to build new underground transportation systems and Hyperloops. This role will primarily be focused on designing and implementing tools to operate, analyze and control The Boring Company's TBMs. Within this role, you will have wide exposure to the overall system architecture.ResponsibilitiesSupport software engineering & controls team writing code for tunnel boring machineDesign and implement tunnel boring HMIsOwnership of data pipelineVisualize relevant data for different stakeholders using dashboards (e.g., Grafana)Support and improve built pipelineBasic QualificationsBachelor’s Degree in Computer Science, Software Engineering, or equivalent fieldExperience developing software applications in Python, C++ or similar high-level languageDevelopment experience in JavaScript, CSS and HTMLFamiliar with using SQL and NoSQL (time series) databasesExperience using git or similar versioning tools for developmentAbility and motivation to learn new skills rapidlyCapable of working with imperfect informationPreferred Skills and ExperienceExcellent communication and teamwork skillsExperience in designing and testing user interfacesKnowledge of the protocols HTTP and MQTTExperience using and configuring CI/CD pipelines and in writing unit testsExperience working in Windows and Linux operating systemsWork experience in agile teams is a plusAdditional RequirementsAbility to work long hours and weekends as necessaryReporting Location: Bastrop, Texas - HeadquartersCultureWe're a team of dedicated, smart, and scrappy people. Our employees are passionate about our mission and determined to innovate at every opportunity.BenefitsWe offer employer-paid medical, dental, and vision coverage, a 401(k) plan, paid holidays, paid vacation, and a competitive amount of equity for all permanent employees.The Boring Company is an Equal Opportunity Employer; employment with The Boring Company is governed on the basis of merit, competence and qualifications and will not be influenced in any manner by race, color, religion, gender, national origin/ethnicity, veteran status, disability status, age, sexual orientation, gender identity, marital status, mental or physical disability or any other legally protected status.",
                "job_type": null,
                "compensation": null,
                "date_posted": "2023-04-18T00:00:00"
            }
        ],
        "total_results": 1000,
        "returned_results": 3
    },
    "indeed": {
        "success": true,
        "error": null,
        "jobs": [
            {
                "title": "Server Engineer",
                "company_name": "Sonic Healthcare USA, Inc",
                "job_url": "https://www.indeed.com/jobs/viewjob?jk=9fb2bea89374ca98",
                "location": {
                    "country": "US",
                    "city": "Austin",
                    "state": "TX",
                    "postal_code": "78716",
                    "address": null
                },
                "description": "Job Functions, Duties, Responsibilities and Position Qualifications: Position Summary: The Server Engineer is responsible for the design, implementation, maintenance, and support for large scale enterprise Microsoft and/or Apple devices including servers, computers, and mobile devices. The Server Engineer is expected to have a strong foundation of Windows Server 2019/2016/2012 operating systems. Knowledge to support MacOS/iOS is beneficial. Proficiency with VM infrastructure, Active Directory, DNS, Mobile Device Management, and/or Windows 10 should also be demonstrated. The Server Engineer must have strong technical, analytical and problem-solving abilities for management and administration of corporate environments. Day-to-day responsibilities include system administration and monitoring of systems, security, performance, backup/restore and configuration changes. The Server Engineer will troubleshoot incidents, determine root causes, and find/implement solutions for problems. They will assist with the implementation of new or additional technology to improve infrastructure service locally and remotely. Essential Functions: Installs, configures and maintains Windows Server 2022/2019/2016/2012, Windows 10, Mac and iOS devices used in the SHUSA infrastructure. Performs daily support of the Windows Server and occasionally Apple environment. Uses common Windows system administration and AD tools to Support and troubleshoot Windows server applications and Mac applications/platforms developed in-house and externally. Thoroughly understands business needs and ensure comprehensive testing scenarios are documented. Serves as the lead technical resource on complex systems projects. Guides and trains less-experienced colleagues. Models excellence in documentation of systems and solutions. Tests and implements projects in accordance with written business and functional design documents and following established standards. Delivers assignments within specified time frames, adhering to all established methodologies, standards and guidelines individually or as a member of a project team. Reports, monitors and verifies system defects, as necessary. Ensures that defects in the products have been corrected and document results of testing. Provides ownership and accountability for assigned testing, keeping supervisor aware of progress and risk. Responds to after hour pages and participates in rotational on-call schedule. Participates in process improvement projects. Acts as second-in-command to Windows Server Manager in their absence. Skills: Confidence and experience in using the typical Windows and/or Mac software and management tools Ability to effectively prioritize and execute tasks in a high-pressure environment. Possesses strong analytical and problem solving skills, including application and network-level troubleshooting ability. Ability to work independently or in teams and manage multiple assignments simultaneously Ability to develop business relationships and communicate effectively with the developers, peers and supervisors. Strong understanding of various protocols and services including NFS, DHCP, DNS, IP, TCP, UDP, TFTP, NTP. Experience with group policy objects on domain servers. Ability to use data and logic to quickly find solutions to difficult challenges. Adheres to schedules and agendas and respects others’ time. Adjusts effectively to new work demands, processes, structures and cultures. Excellent written, oral, interpersonal, and presentational skills. Knowledge of Healthcare Information Technology Education, Licensure, Certification / Job Qualifications: Bachelor (4-year) degree with a technical major such as engineering or computer science, or demonstrated work experience. Microsoft MCSE Certification or VMware VCP would be a plus. Apple certifications would be a plus. Physical Requirements: Sitting for extended periods of time. Dexterity of hands and fingers to operate a computer keyboard, mouse and to handle other computer components. Occasional lifting and transporting of moderately heavy objects, such as computers and peripherals up to 30lbs. Light to moderate physical effort (lift/carry up to 50 lbs.) Occasional reaching, stooping, bending, kneeling and crouching. Occasional carrying, pushing, and pulling of objects. Frequent, prolonged standing/sitting/walking. Extensive computer work. Frequent use of telephone. Occasional travel required to interact with Division personnel and/or attend meetings or educational training. Environmental Conditions: Work involves intermittent to occasional exposure to unpleasant working conditions or undesirable elements; may involve some contact with potentially hazardous or harmful elements in providing administrative or support services. Scheduled Weekly Hours: 40 Work Shift: Job Category: Information Technology Company: Sonic Healthcare USA, Inc Sonic Healthcare USA is an equal opportunity employer that celebrates diversity and is committed to an inclusive workplace for all employees. We prohibit discrimination and harassment of any kind based on race, color, sex, religion, age, national origin, disability, genetics, veteran status, sexual orientation, gender identity or expression, or any other characteristic protected by federal, state, or local laws.",
                "job_type": "fulltime",
                "compensation": null,
                "date_posted": "2023-08-15T00:00:00"
            },
            {
                "title": "Firmware Engineer",
                "company_name": "Great River Technology",
                "job_url": "https://www.indeed.com/jobs/viewjob?jk=d98ff534bc583502",
                "location": {
                    "country": "US",
                    "city": "",
                    "state": "TX",
                    "postal_code": null,
                    "address": null
                },
                "description": "Electronic Hardware Engineer Great River Technology is looking for a highly motivated Electronic Hardware Engineer to join its Albuquerque team in the development of high-performance digital video products. Job Responsibilities The Electronic Hardware Engineer will work in teams of 3 to 5 people responsible for the realization of the Great River's video products and firmware IP cores. He or she will also work directly with customers to resolve technical problems. Minimum Requirements The ideal candidate will have: A 4-year Engineering degree Experience with VHDL logic design, VHDL test benches and simulation Familiarity with Xilinx ISE/Vivado, Altera Quartus, and/or ModelSim is a plus. About Great River Great River Technology is an employee owned company in Albuquerque, New Mexico, that specializes in mission-critical, high- performance digital video development tools and services for commercial aerospace and military customers. We have off-the-shelf board-level products for high-speed video links and point-to-point data transmission. Great River offers competitive pay and generous benefits - including company stock, and performance bonuses. Work environment Great River is a small entrepreneurial company with a friendly, team-oriented work atmosphere. EEO statement Great River Technology is an equal opportunity employer. Job Type: Full-time Pay: $69,904.00 - $152,749.00 per year Benefits: 401(k) Dental insurance Health insurance Paid time off Schedule: 8 hour shift Monday to Friday Supplemental pay types: Bonus pay Ability to commute/relocate: Albuquerque, NM 87113: Reliably commute or planning to relocate before starting work (Required) Education: Bachelor's (Required) Experience: VHDL Coding: 1 year (Required) Work Location: In person",
                "job_type": "fulltime",
                "compensation": {
                    "interval": "yearly",
                    "min_amount": 152749.0,
                    "max_amount": 69904.0,
                    "currency": "USD"
                },
                "date_posted": "2022-03-21T00:00:00"
            },
            {
                "title": "Software Engineer",
                "company_name": "INTEL",
                "job_url": "https://www.indeed.com/jobs/viewjob?jk=a2cfbb98d2002228",
                "location": {
                    "country": "US",
                    "city": "Austin",
                    "state": "TX",
                    "postal_code": null,
                    "address": null
                },
                "description": "Job Description Designs, develops, tests, and debugs software tools, flows, PDK design components, and/or methodologies used in design automation and by teams in the design of hardware products, process design, or manufacturing. Responsibilities include capturing user stories/requirements, writing both functional and test code, automating build and deployment, and/or performing unit, integration, and endtoend testing of the software tools. #DesignEnablement Qualifications Minimum qualifications are required to be initially considered for this position. Preferred qualifications are in addition to the minimum requirements and are considered a plus factor in identifying top candidates. Minimum Qualifications: Candidate must possess a BS degree with 6+ years of experience or MS degree with 4+ years of experience or PhD degree with 2+ years of experience in Computer Engineering, EE, Computer Science, or relevant field. 3+ years of experience in the following: Database structure and algorithms. C or C++ software development. Scripting in Perl or Python or TCL. ICV-PXL or Calibre SVRF or Physical Verification runset code development. Preferred Qualifications: 3+ years of experience in the following: Agile/Test-Driven Development. Semiconductor Devices, device physics or RC Extraction. RC Modeling or Electrostatics or Field Solver development Inside this Business Group As the world's largest chip manufacturer, Intel strives to make every facet of semiconductor manufacturing state-of-the-art - from semiconductor process development and manufacturing, through yield improvement to packaging, final test and optimization, and world class Supply Chain and facilities support. Employees in the Technology Development and Manufacturing Group are part of a worldwide network of design, development, manufacturing, and assembly/test facilities, all focused on utilizing the power of Moore’s Law to bring smart, connected devices to every person on Earth. Other Locations US, TX, Austin; US, CA, Folsom; US, CA, Santa Clara Covid Statement Intel strongly encourages employees to be vaccinated against COVID-19. Intel aligns to federal, state, and local laws and as a contractor to the U.S. Government is subject to government mandates that may be issued. Intel policies for COVID-19 including guidance about testing and vaccination are subject to change over time. Posting Statement All qualified applicants will receive consideration for employment without regard to race, color, religion, religious creed, sex, national origin, ancestry, age, physical or mental disability, medical condition, genetic information, military and veteran status, marital status, pregnancy, gender, gender expression, gender identity, sexual orientation, or any other characteristic protected by local law, regulation, or ordinance. Benefits We offer a total compensation package that ranks among the best in the industry. It consists of competitive pay, stock, bonuses, as well as, benefit programs which include health, retirement, and vacation. Find more information about all of our Amazing Benefits here: https://www.intel.com/content/www/us/en/jobs/benefits.html Annual Salary Range for jobs which could be performed in US, California: $139,480.00-$209,760.00 Salary range dependent on a number of factors including location and experience Working Model This role will be eligible for our hybrid work model which allows employees to split their time between working on-site at their assigned Intel site and off-site. In certain circumstances the work model may change to accommodate business needs. JobType Hybrid",
                "job_type": "fulltime",
                "compensation": {
                    "interval": "yearly",
                    "min_amount": 209760.0,
                    "max_amount": 139480.0,
                    "currency": "USD"
                },
                "date_posted": "2023-08-18T00:00:00"
            }
        ],
        "total_results": 845,
        "returned_results": 3
    },
    "zip_recruiter": {
        "success": true,
        "error": null,
        "jobs": [
            {
                "title": "Software Developer II (Web-Mobile) - Remote",
                "company_name": "Navitus Health Solutions LLC",
                "job_url": "https://www.ziprecruiter.com/jobs/navitus-health-solutions-llc-1a3cba76/software-developer-ii-web-mobile-remote-aa2567f2?zrclid=51525b13-a008-4f46-8cf0-67dae6044408&lvk=NKzmQn2kG7L1VJplTh5Cqg.--N2aTr3mbB",
                "location": {
                    "country": "US",
                    "city": "Austin",
                    "state": "TX",
                    "postal_code": null,
                    "address": null
                },
                "description": "Putting People First in Pharmacy- Navitus was founded as an alternative to traditional pharmacy benefit manager (PBM) models. We are committed to removing cost from the drug supply chain to make medications more affordable for the people who need them. At Navitus, our team members work in an environment that celebrates diversity, fosters creativity and encourages growth. We welcome new ideas and share a passion for excellent service to our customers and each other. The Software Developer II ensures efforts are in alignment with the IT Member Services to support customer-focused objectives and the IT Vision, a collaborative partner delivering innovative ideas, solutions and services to simplify people’s lives. The Software Developer II’s role is to define, develop, test, analyze, and maintain new software applications in support of the achievement of business requirements. This includes writing, coding, testing, and analyzing software programs and applications. The Software Developer will also research, design, document, and modify software specifications throughout the production life cycle.Is this you? Find out more below! How do I make an impact on my team?Collaborate with developers, programmers, and designers in conceptualizing and development of new software programs and applications.Analyze and assess existing business systems and procedures.Design, develop, document and implement new applications and application enhancements according to business and technical requirementsAssist in defining software development project plans, including scoping, scheduling, and implementation.Conduct research on emerging application development software products, languages, and standards in support of procurement and development efforts.Liaise with internal employees and external vendors for efficient implementation of new software products or systems and for resolution of any adaptation issues.Recommend, schedule, and perform software improvements and upgrades.Write, translate, and code software programs and applications according to specifications.Write programming scripts to enhance functionality and/or performance of company applications as necessary.Design, run and monitor software performance tests on new and existing programs for the purposes of correcting errors, isolating areas for improvement, and general debugging to deliver solutions to problem areas.Generate statistics and write reports for management and/or team members on the status of the programming process.Develop and maintain user manuals and guidelines and train end users to operate new or modified programs.Install software products for end users as required.Responsibilities (working knowledge of several of the following):Programming LanguagesC#HTML/HTML5CSS/CSS3JavaScriptAngularReact/NativeRelation DB development (Oracle or SQL Server) Methodologies and FrameworksASP.NET CoreMVCObject Oriented DevelopmentResponsive Design ToolsVisual Studio or VSCodeTFS or other source control softwareWhat our team expects from you? College diploma or university degree in the field of computer science, information systems or software engineering, and/or 6 years equivalent work experienceMinimum two years of experience requiredPractical experience working with the technology stack used for Web and/or Mobile Application developmentExcellent understanding of coding methods and best practices.Experience interviewing end-users for insight on functionality, interface, problems, and/or usability issues.Hands-on experience developing test cases and test plans.Healthcare industry practices and HIPAA knowledge would be a plus.Knowledge of applicable data privacy practices and laws.Participate in, adhere to, and support compliance program objectivesThe ability to consistently interact cooperatively and respectfully with other employeesWhat can you expect from Navitus?Hours/Location: Monday-Friday 8:00am-5:00pm CST, Appleton WI Office, Madison WI Office, Austin TX Office, Phoenix AZ Office or RemotePaid Volunteer HoursEducational Assistance Plan and Professional Membership assistanceReferral Bonus Program – up to $750!Top of the industry benefits for Health, Dental, and Vision insurance, Flexible Spending Account, Paid Time Off, Eight paid holidays, 401K, Short-term and Long-term disability, College Savings Plan, Paid Parental Leave, Adoption Assistance Program, and Employee Assistance Program",
                "job_type": "fulltime",
                "compensation": {
                    "interval": "yearly",
                    "min_amount": 75000.0,
                    "max_amount": 102000.0,
                    "currency": "US"
                },
                "date_posted": "2023-07-22T00:49:06+00:00"
            },
            {
                "title": "Senior Software Engineer",
                "company_name": "Macpower Digital Assets Edge (MDA Edge)",
                "job_url": "https://www.ziprecruiter.com/jobs/macpower-digital-assets-edge-mda-edge-3205cee9/senior-software-engineer-59332966?zrclid=f2e8377d-33f6-4398-99e5-e3ea0c64234a&lvk=wEF8NWo_yJghc-buzNmD7A.--N2aWoMMcN",
                "location": {
                    "country": "US",
                    "city": "Austin",
                    "state": "TX",
                    "postal_code": null,
                    "address": null
                },
                "description": "Job Summary: As a senior software engineer, you will be a key player in building and contributing to our platform and product roadmap, shaping our technology strategy, and mentoring talented engineers. You are motivated by being apart of effective engineering teams and driven to roll up your sleeves and dive into code when necessary. Being hands on with code is critical for success in this role. 80-90% of time will be spent writing actual code. Our engineering team is hybrid and meets in-person (Austin, TX) 1-2 days a week. Must haves: Background: 5+ years in software engineering with demonstrated success working for fast-growing companies. Success in building software from the ground up with an emphasis on architecture and backend programming. Experience developing software and APIs with technologies like TypeScript, Node.js, Express, NoSQL databases, and AWS. Nice to haves: Domain expertise: Strong desire to learn and stay up-to-date with the latest user-facing security threats and attack methods. Leadership experience is a plus. 2+ years leading/managing teams of engineers. Ability to set and track goals with team members, delegate intelligently. Project management: Lead projects with a customer-centric focus and a passion for problem-solving.",
                "job_type": "fulltime",
                "compensation": {
                    "interval": "yearly",
                    "min_amount": 140000.0,
                    "max_amount": 140000.0,
                    "currency": "US"
                },
                "date_posted": "2023-07-21T09:17:19+00:00"
            },
            {
                "title": "Software Developer II- remote",
                "company_name": "Navitus Health Solutions LLC",
                "job_url": "https://www.ziprecruiter.com/jobs/navitus-health-solutions-llc-1a3cba76/software-developer-ii-remote-a9ff556a?zrclid=86334c0f-c0cb-4252-b078-17f3d8079964&lvk=Oz2MG9xtFwMW6hxOsCrtJw.--N2cr_mA0F",
                "location": {
                    "country": "US",
                    "city": "Austin",
                    "state": "TX",
                    "postal_code": null,
                    "address": null
                },
                "description": "Putting People First in Pharmacy- Navitus was founded as an alternative to traditional pharmacy benefit manager (PBM) models. We are committed to removing cost from the drug supply chain to make medications more affordable for the people who need them. At Navitus, our team members work in an environment that celebrates diversity, fosters creativity and encourages growth. We welcome new ideas and share a passion for excellent service to our customers and each other. The Software Developer II ensures efforts are in alignment with the IT Health Strategies Team to support customer-focused objectives and the IT Vision, a collaborative partner delivering innovative ideas, solutions and services to simplify people’s lives. The Software Developer IIs role is to define, develop, test, analyze, and maintain new and existing software applications in support of the achievement of business requirements. This includes designing, documenting, coding, testing, and analyzing software programs and applications. The Software Developer will also research, design, document, and modify software specifications throughout the production life cycle.Is this you? Find out more below! How do I make an impact on my team?Provide superior customer service utilizing a high-touch, customer centric approach focused on collaboration and communication.Contribute to a positive team atmosphere.Innovate and create value for the customer.Collaborate with analysts, programmers and designers in conceptualizing and development of new and existing software programs and applications.Analyze and assess existing business systems and procedures.Define, develop and document software business requirements, objectives, deliverables, and specifications on a project-by-project basis in collaboration with internal users and departments.Design, develop, document and implement new applications and application enhancements according to business and technical requirements.Assist in defining software development project plans, including scoping, scheduling, and implementation.Research, identify, analyze, and fulfill requirements of all internal and external program users.Recommend, schedule, and perform software improvements and upgrades.Consistently write, translate, and code software programs and applications according to specifications.Write new and modify existing programming scripts to enhance functionality and/or performance of company applications as necessary.Liaise with network administrators, systems analysts, and software engineers to assist in resolving problems with software products or company software systems.Design, run and monitor software performance tests on new and existing programs for the purposes of correcting errors, isolating areas for improvement, and general debugging.Administer critical analysis of test results and deliver solutions to problem areas.Generate statistics and write reports for management and/or team members on the status of the programming process.Liaise with vendors for efficient implementation of new software products or systems and for resolution of any adaptation issues.Ensure target dates and deadlines for development are met.Conduct research on emerging application development software products, languages, and standards in support of procurement and development efforts.Develop and maintain user manuals and guidelines.Train end users to operate new or modified programs.Install software products for end users as required.Participate in, adhere to, and support compliance program objectives.Other related duties as assigned/required.Responsibilities (including one or more of the following):VB.NETC#APIFast Healthcare Interoperability Resources (FHIR)TelerikOracleMSSQLVisualStudioTeamFoundation StudioWhat our team expects from you? College diploma or university degree in the field of computer science, information systems or software engineering, and/or 6 years equivalent work experience.Minimum two years of experience requiredExcellent understanding of coding methods and best practices.Working knowledge or experience with source control tools such as TFS and GitHub.Experience interviewing end-users for insight on functionality, interface, problems, and/or usability issues.Hands-on experience developing test cases and test plans.Healthcare industry practices and HIPAA knowledge would be a plus.Knowledge of applicable data privacy practices and laws.Participate in, adhere to, and support compliance program objectivesThe ability to consistently interact cooperatively and respectfully with other employeesWhat can you expect from Navitus?Hours/Location: Monday-Friday remote Paid Volunteer HoursEducational Assistance Plan and Professional Membership assistanceReferral Bonus Program – up to $750!Top of the industry benefits for Health, Dental, and Vision insurance, Flexible Spending Account, Paid Time Off, Eight paid holidays, 401K, Short-term and Long-term disability, College Savings Plan, Paid Parental Leave, Adoption Assistance Program, and Employee Assistance Program",
                "job_type": "fulltime",
                "compensation": {
                    "interval": "yearly",
                    "min_amount": 75000.0,
                    "max_amount": 102000.0,
                    "currency": "US"
                },
                "date_posted": "2023-07-10T20:44:25+00:00"
            }
        ],
        "total_results": 3798,
        "returned_results": 3
    }
}
</code></pre>
</details>

## Installation
_Python >= 3.10 required_  
1. Clone this repository `git clone https://github.com/cullenwatson/jobspy`
2. Install the dependencies with `pip install -r requirements.txt`
4. Run the server with `uvicorn main:app --reload`

## Usage

To see the interactive API documentation, visit [localhost:8000/docs](http://localhost:8000/docs).

For Postman integration:
- Import the Postman collection and environment JSON files from the `/postman/` folder.


## FAQ

### I'm having issues with my queries. What should I do?

Broadening your filters can often help. Additionally, try reducing the number of `results_wanted`.  
If issues still persist, feel free to submit an issue.

### How to enable auth?

Change `AUTH_REQUIRED` in `/settings.py` to `True`

The auth uses [supabase](https://supabase.com). Create a project with a `users` table and disable RLS.  
  
<img src="https://github.com/cullenwatson/jobspy/assets/78247585/03af18e1-5386-49ad-a2cf-d34232d9d747" width="500">


Add these three environment variables:

- `SUPABASE_URL`: go to project settings -> API -> Project URL  
- `SUPABASE_KEY`: go to project settings -> API -> service_role secret
- `JWT_SECRET_KEY` - type `openssl rand -hex 32` in terminal to create a 32 byte secret key

Use these endpoints to register and get an access token: 

![image](https://github.com/cullenwatson/jobspy/assets/78247585/c84c33ec-1fe8-4152-9c8c-6c4334aecfc3)

