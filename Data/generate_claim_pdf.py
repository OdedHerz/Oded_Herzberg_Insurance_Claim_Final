"""
Insurance Claim PDF Generator - 13 Pages
Generates a comprehensive synthetic insurance claim document with timeline-based events.
Each page contains exactly ~2000 characters for optimal chunking (5 chunks per page with 400 char chunks, 50 overlap).
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import json
from datetime import datetime

def create_claim_content():
    """Generate the insurance claim content for 13 pages with metadata."""
    
    # Page 1: Overview - Introduction (type: Overview)
    page1 = {
        "header": "Claim Introduction and Overview",
        "date": "2024-01-15",
        "involved_parties": ["Sarah Mitchell", "Progressive Auto Insurance", "Claims Department"],
        "type": "Overview",
        "text": """This insurance claim is filed under claim number CLM-2024-00789-AUTO and policy number PAI-8847562-2023. The claim was officially submitted on January 15, 2024, at 14:32:17 hours through Progressive Auto Insurance. The policyholder is Sarah Mitchell, age 34, residing at 4582 Birch Lane, Seattle, Washington 98102. She holds a Comprehensive Auto Insurance policy covering her 2022 Honda Accord with vehicle identification number 1HGCV1F3XNA123456. The policy was initiated on March 15, 2023, and includes coverage of $500,000 for liability claims, $100,000 for collision damage, $50,000 for uninsured motorist protection, and $25,000 medical payments coverage. A multi-vehicle collision occurred on January 15, 2024, at 09:23:45 AM at the intersection of Maple Avenue and 5th Street in Seattle, Washington 98101. The incident involved three vehicles: Mitchell's insured Honda Accord, a 2019 Toyota Camry driven by Robert Chen, and a parked 2020 Ford F-150 owned by James Rodriguez. The collision resulted in significant property damage to all three vehicles and minor personal injuries requiring medical attention and police investigation. Initial damage assessment conducted by certified insurance adjusters estimates total claim value at $47,850, consisting of $44,010 for vehicle repairs and $3,840 for medical expenses. The incident occurred during morning rush hour with wet road surfaces from overnight rainfall accumulating 0.3 inches. Temperature was 42 degrees Fahrenheit with reduced visibility of 200 feet. All parties provided statements to investigating officers. Traffic camera footage and dashboard recordings provide conclusive evidence for liability determination. The claim processing follows standard procedures with expected resolution in 15-20 business days."""
    }
    
    # Page 2: Event 1 - Initial Collision (type: Details)
    page2 = {
        "header": "Initial Collision Dynamics",
        "date": "2024-01-15 09:23:45",
        "involved_parties": ["Sarah Mitchell", "Robert Chen", "Seattle Police Department", "Officer James Wilson"],
        "type": "Details",
        "text": """The collision event commenced on January 15, 2024, at 09:23:45 AM PST. The precise geolocation of the impact was recorded via the claimant's onboard telematics system at coordinates 47.6062° N Latitude and 122.3321° W Longitude, corresponding to the urban intersection of Maple Avenue and 5th Street, Seattle, WA 98101. This intersection is designated as a High-Volume Traffic Control Point (HV-TCP) ID# SEA-INT-442, managing an Average Daily Traffic (ADT) volume of 28,500 units. The intersection infrastructure includes standard four-way traffic signals manufactured by Siemens Mobility, synced to the municipal timing grid. Sarah Mitchell (Unit 1) was operating her vehicle northbound on Maple Avenue in Lane 2 (center lane) at a velocity of 25 miles per hour, consistent with the moderate flow of morning rush hour traffic. The traffic control signal governing her lane displayed a solid Green phase, authorizing right-of-way. Simultaneously, Mr. Robert Chen (Unit 2), operating the 2019 Toyota Camry (Plate: WA-ABC-1234), was traveling eastbound on 5th Street. According to Engine Control Module (ECM) data retrieved post-incident, Unit 2 entered the intersection at a speed of 45 mph in a zone posted for 30 mph. At timestamp 09:23:44, municipal security camera SC-882 captured Unit 2 entering the intersection 2.3 seconds after the traffic signal for eastbound traffic had transitioned to Red phase. Unit 2 failed to decelerate and struck Unit 1. The primary point of impact (POI) was the driver's side front quarter panel of Mitchell's Honda Accord. The kinetic energy transfer caused severe structural deformation, including the collapse of the A-pillar and crushing of the left front fender. The force of impact induced a counter-clockwise rotational yaw of approximately 45 degrees to Unit 1. Following the initial rotational force, Unit 1 was deflected into a secondary collision with Unit 3, a legally parked 2020 Ford F-150 (Plate: WA-XYZ-7890) located 12 feet from the intersection corner. The secondary impact occurred at the right rear bumper of Unit 1. Within milliseconds of the primary impact (09:23:46), the Supplemental Restraint System (SRS) in the Honda Accord deployed the driver's front and side-curtain airbags. Ms. Mitchell immediately exhibited signs of deceleration trauma, self-reporting neck pain measuring 6/10 on the visual analog pain scale, alongside dizziness and spatial disorientation. Both vehicle operators remained at the scene in compliance with RCW 46.52.020."""
    }
    
    # Page 3: Event 2 - Emergency Response (type: Details)
    page3 = {
        "header": "Emergency Response and Triage",
        "date": "2024-01-15 09:31:22",
        "involved_parties": ["Seattle Fire Department", "Medic Unit 47", "Paramedic Jennifer Ross", "Officer James Wilson"],
        "type": "Details",
        "text": """The Seattle Emergency Communications Center (911) received the initial distress call at 09:23:45 AM from an automated eCall system, followed by a bystander voice call at 09:24:33. Dispatch authorized a priority response. First responders arrived on the scene at 09:31:22 AM, establishing a response time of 7 minutes and 37 seconds. The response team consisted of Seattle Fire Department (SFD) Engine 10, commanded by Captain David Morrison (Badge #4492) with a crew of four firefighters, and King County Medic Unit 47 staffed by two paramedics. Concurrent police support was provided by Seattle Police Department (SPD) Unit 3-Adam-12, operated by Officers James Wilson (Badge #8821) and Maria Gonzalez (Badge #5593). Lead Paramedic Jennifer Ross (NREMT-P License #WA-99283) initiated the primary medical assessment of Ms. Mitchell at 09:33:00. Standard trauma protocols were observed. The initial set of vital signs recorded at 09:34:15 indicated physiological stress: Blood Pressure was elevated at 145/92 mmHg (Hypertensive response), Heart Rate was Tachycardic at 98 beats per minute, Respiratory Rate was 18 breaths per minute, and Oxygen Saturation (SpO2) was 98 percent on ambient air. Body temperature was 98.4°F. A Neurological assessment confirmed the patient was Alert and Oriented x4 (Person, Place, Time, Event), yielding a Glasgow Coma Scale (GCS) score of 15/15. Despite the stable GCS score, Ms. Mitchell presented with subjective complaints of acute cervical pain radiating to the trapezius muscle group. Physical palpation revealed tenderness at the C3-C6 vertebral levels. Range of Motion (ROM) in the cervical spine was significantly restricted due to muscle guarding. She also reported a headache rated 6/10 severity. To prevent potential spinal cord injury, a rigid cervical collar (C-Collar) was applied, and she was extricated onto a backboard for transport. Simultaneously, Officer Wilson secured the physical scene at 09:32:00. A safety perimeter measuring 50 feet was established using standard reflective traffic cones and barricade tape. Photographic evidence (Digital Series SPD-2024-0156-IMG) was captured, documenting 47 feet of skid marks originating from the trajectory of Mr. Chen's vehicle. These marks were analyzed against the wet pavement conditions. Officer Gonzalez retrieved the traffic loop data and camera footage, which definitively confirmed the traffic signal violation (RCW 46.61.050) by the adverse driver."""
    }
    
    # Page 4: Event 3 - Medical Evaluation (type: Details)
    page4 = {
        "header": "Hospitalization and Diagnosis",
        "date": "2024-01-15 14:45:18",
        "involved_parties": ["Dr. Michael Patterson", "Sarah Mitchell", "Claims Adjuster Linda Martinez"],
        "type": "Details",
        "text": """Ms. Mitchell was transported via King County Ambulance Service (Unit A-412) to the Seattle Medical Center Level I Trauma Center. The ambulance departed the scene at 09:52:00 and arrived at the Emergency Department bay at 10:15:33 AM. The transport duration was 23 minutes, during which continuous cardiac monitoring was maintained. Upon arrival, she was admitted under patient ID #SMC-2024-99821. She was evaluated by Dr. Michael Patterson, a board-certified emergency physician (Medical License #MD-WA-55421) with 15 years of trauma experience. The evaluation commenced at 14:45:18 hours following initial nurse triage and stabilization. The clinical diagnosis was finalized as a Grade 2 Whiplash Associated Disorder (WAD), characterized by soft tissue injury to the cervical muscles and ligaments. Specific findings included cervical spine strain affecting vertebrae C3 through C6, and a mild concussion (MTBI) presenting with post-concussive symptoms such as photophobia, dizziness, and mild cognitive latency. To rule out osseous or neurological trauma, a Computed Tomography (CT) scan of the cervical spine and head was ordered. The imaging was performed at 15:23:00 hours using a Siemens Healthineers Somatom scanner (Protocol: Trauma Head/Neck w/o contrast). The Radiology Report (Ref: RAD-8821) confirmed no acute fractures, no dislocation of the cervical bodies, no intracranial hemorrhage, and no evidence of herniated discs or spinal cord compression. Based on these findings, Dr. Patterson formulated a comprehensive discharge plan. The pharmacological regimen included Ibuprofen 600 mg to be taken orally three times daily with food for inflammation, and Cyclobenzaprine 10 mg (muscle relaxant) to be taken at bedtime to alleviate paravertebral muscle spasms. A soft cervical collar was prescribed for intermittent use over the next 14 days to limit neck rotation. Claims Adjuster Linda Martinez conducted a recorded interview with the patient at 16:30:00. Mitchell provided access to her dashcam footage (File: DASH-2024-01-15.mp4). Police Report SPD-2024-0156 was formally filed at 17:15:00, solidifying the liability determination against Mr. Chen based on the corroborating digital evidence. The total medical invoice for the ER visit was generated at $3,840.00."""
    }
    
    # Page 5: Event 4 - Vehicle Inspection (type: Details)
    page5 = {
        "header": "Technical Damage Assessment",
        "date": "2024-01-16 10:30:00",
        "involved_parties": ["Premier Auto Body Shop", "Inspector Thomas Blake", "Progressive Insurance"],
        "type": "Details",
        "text": """The claimant's vehicle, a 2022 Honda Accord, was transferred via flatbed tow truck to Premier Auto Body Shop (Vendor ID: PAB-992), located at 8245 Industrial Way, Seattle, WA 98108. The vehicle arrived on January 16, 2024, at 10:30:00 AM. Certified Inspector Thomas Blake (ASE Master Technician ID #ASE-4492-T) initiated the damage appraisal. The inspection utilized the Hunter Engineering HawkEye Elite laser alignment and frame measuring system to detect structural deviations. The computerized chassis analysis revealed critical unibody misalignment. Specifically, the driver's side A-pillar sustained a 3.2-inch inward deformation relative to the centerline. The B-pillar reinforcement bracket exhibited stress fractures at the weld points. The front subframe assembly showed a 1.8-inch lateral displacement, mandating a complete replacement to ensure future crashworthiness. The suspension geometry was severely compromised; the left front lower control arm (Part #51350-TVA-A00) had bent mounting points, the outer tie rod end ball joint had separated, and the wheel hub bearing assembly was brinelled from impact shock. Cosmetic and panel damage was extensive: the driver's door skin (Part #67050-TVA-305ZZ) featured deep creasing intrusion, the left front fender was crushed beyond repair, the aluminum hood panel was buckled, and the LED headlight assembly (Part #33100-TVA-A01) was shattered. The estimation logic utilized the CCC ONE appraisal platform. The total cost for Original Equipment Manufacturer (OEM) parts was calculated at $12,450.00. This specification of OEM parts is required by the policy's 'New Car Replacement' endorsement. Labor costs were derived from a standard repair time of 87.5 hours at the contracted regional rate of $95.00 per hour, totaling $8,312.50. This labor includes teardown, structural realignment, refinishing, and reassembly. Ancillary charges included $890.00 for frame rack rental, $2,340.00 for PPG Envirobase High Performance waterborne paint materials (Color Code NH-883P), $185.00 for four-wheel alignment, and $125.00 for post-repair On-Board Diagnostics (OBD-II) scanning. The aggregate repair estimate was certified at $23,102.50 by Independent Appraiser David Richardson."""
    }
    
    # Page 6: Event 5 - Medical Follow-up (type: Details)
    page6 = {
        "header": "Physical Therapy and Rehabilitation",
        "date": "2024-01-22 08:00:00",
        "involved_parties": ["Dr. Michael Patterson", "Sarah Mitchell", "Physical Therapist Amanda Chen"],
        "type": "Details",
        "text": """Ms. Mitchell attended her initial follow-up consultation with Dr. Patterson on January 22, 2024, at 08:00:00 AM, marking the one-week post-collision milestone. The clinical re-evaluation noted persistent cervical spine tenderness, though the acute inflammatory phase had subsided. Dr. Patterson utilized a goniometer to measure the current active Range of Motion (ROM). Results indicated significant limitations: Right Rotation was 45 degrees (Normal: 80), Left Rotation was 42 degrees (Normal: 80), Flexion was 35 degrees (Normal: 50), and Extension was 40 degrees (Normal: 60). The patient's self-reported pain index had improved from a baseline of 6/10 to 4/10. Neurological testing of the upper extremities, including Deep Tendon Reflexes (DTR) at the Biceps (C5), Brachioradialis (C6), and Triceps (C7), yielded normal 2+ grades bilaterally. Muscle strength grading was 5/5 in all groups, ruling out radiculopathy. Based on these metrics, Dr. Patterson signed a referral (Ref: RX-PT-2024-882) for a course of Physical Therapy. The prescription mandated 12 sessions over a six-week period at Seattle Rehabilitation Center. The treatment plan focuses on restoration of cervical mobility, strengthening of the deep neck flexors, and scapular stabilization. Physical Therapist Amanda Chen (DPT License #PT-WA-11029) conducted the intake session on January 22 at 14:30:00. Ms. Chen administered the Neck Disability Index (NDI) questionnaire, on which Mitchell scored a 28/50, categorizing the impairment as 'Moderate Disability'. The 60-minute therapeutic session included: (1) 15 minutes of moist heat application using hydrocollator packs at 165°F to increase tissue elasticity; (2) Grade I and II Maitlands manual joint mobilization to the cervical facet joints; (3) Soft tissue mobilization using myofascial release techniques; and (4) Transcutaneous Electrical Nerve Stimulation (TENS) applied at 100Hz for pain gating. Mitchell was instructed on a Home Exercise Program (HEP) consisting of chin tucks and levator scapulae stretches to be performed twice daily. Work restrictions were updated to 'Modified Duty', limiting lifting to 10 lbs and requiring ergonomic breaks every 30 minutes."""
    }
    
    # Page 7: Event 6 - Witness Statements (type: Details)
    page7 = {
        "header": "Witness Testimony and Traffic Engineering",
        "date": "2024-01-15 11:45:00",
        "involved_parties": ["Marcus Thompson", "Seattle Police", "Traffic Engineer Dr. Susan Miller"],
        "type": "Details",
        "text": """Crucial to the liability determination was the sworn testimony of an independent eyewitness, Mr. Marcus Thompson. Thompson, a 42-year-old accountant, was standing at the designated King County Metro bus stop on the southeast corner of the intersection at the time of the incident (approx. 35 feet from the point of impact). He provided a recorded statement to Officer Wilson at 11:45:00 AM on January 15, 2024, assigned Statement ID #WT-2024-0156-001. In his statement, Thompson attested: 'I was checking my watch at 09:23:40. I looked up and saw the northbound light was green. The Toyota (Chen's vehicle) was coming fast, maybe 45 or 50. The light for him had been red for a good two or three seconds. I saw his brake lights come on only after he was already in the box (intersection).' Thompson signed the affidavit under penalty of perjury. To scientifically validate this timeline, Dr. Susan Miller, Senior Traffic Engineer for the Seattle Department of Transportation (SDOT), performed a signal timing analysis on January 16. Her report (Eng-Report #SDOT-sig-992) confirmed the signal phasing plan for Intersection 442. The cycle length is fixed at 90 seconds. The Northbound Green phase duration is 35 seconds, followed by a 5-second Yellow clearance and a 3-second All-Red safety buffer. The Eastbound control follows the same pattern. Review of the Controller Logs from the traffic cabinet verified that the signal hardware was functioning within NEMA TS-2 standards with no faults recorded. Furthermore, the SPD Video Forensics Team analyzed the raw footage from the municipal camera. Frame-by-frame decomposition revealed that the traffic signal governing Mr. Chen's lane transitioned to Solid Red at timestamp 09:23:42.850. Mr. Chen's vehicle crossed the stop bar limit line at timestamp 09:23:45.127. This calculates to a precise Red Light Violation of 2.277 seconds. This objective data irrefutably corroborates Mr. Thompson's subjective observations and establishes the proximate cause of the collision as the failure of Unit 2 to yield the right of way."""
    }
    
    # Page 8: Event 7 - Financial Breakdown (type: Details)
    page8 = {
        "header": "Comprehensive Financial Analysis",
        "date": "2024-01-17 09:00:00",
        "involved_parties": ["Progressive Auto Insurance", "Claims Adjuster Linda Martinez", "Finance Department"],
        "type": "Details",
        "text": """On January 17, 2024, at 09:00:00 AM, Senior Claims Adjuster Linda Martinez finalized the financial reserving and payment schedule for Claim CLM-2024-00789-AUTO. This process involved the reconciliation of all vendor invoices against the coverage limits of Policy PAI-8847562-2023. The financial exposure is categorized into three primary ledgers: Collision Coverage (Vehicle), Medical Payments (Injury), and Loss Adjustment Expenses (LAE). 1. VEHICLE DAMAGE LEDGER: The gross approved repair cost is $23,102.50, payable to Premier Auto Body. This includes the supplementary check for the A-pillar reinforcement. Rental reimbursement is authorized for 18 days at a negotiated rate of $65.00/day (Enterprise Rent-A-Car Contract #E-99281), totaling $1,170.00. Towing and storage fees charged by Mac's Towing amounted to $485.00 ($285.00 base tow + $200.00 for 3 days storage). A Diminished Value (DV) settlement of $18,400.00 was calculated using the 17c Formula, acknowledging the impact of severe structural damage on the vehicle's resale value. Administrative fees for claim file management totaled $852.50. The Gross Vehicle Damage amount is $44,010.00. Applying the policyholder's $500.00 deductible, the Net Payout for property damage is $43,510.00. 2. MEDICAL PAYMENTS LEDGER: Coverage limit is $25,000.00. Approved expenses include the Seattle Medical Center ER invoice of $1,250.00 (Facility Fee Code 99285), Radiology invoice for CT Scans at $890.00 (CPT Code 70450), and Physician Services at $625.00. The Physical Therapy block grant for 12 sessions at $95.00/session totals $1,140.00. Pharmacy reimbursements for Ibuprofen and Cyclobenzaprine total $185.00. Records retrieval fees were $50.00. Total Medical Payout: $3,840.00. 3. TOTAL CLAIM VALUE: Combining the Vehicle Ledger ($44,010.00) and Medical Ledger ($3,840.00), the Total Claim Value is certified at $47,850.00. All payments were queued for Electronic Funds Transfer (EFT). The vehicle repair payment (Batch #EFT-2024-02-00789) was scheduled for February 2, 2024. The medical provider payments were scheduled for batch processing on February 3, 2024. This total falls well within the aggregate policy limit of $100,000.00 for property and $25,000.00 for medical, requiring no excess layer triggering."""
    }
    
    # Page 9: Event 8 - Repair Coordination (type: Details)
    page9 = {
        "header": "Parts Procurement and Repair Execution",
        "date": "2024-01-19 08:30:00",
        "involved_parties": ["Premier Auto Body Shop", "Thomas Blake", "Honda Parts Department"],
        "type": "Details",
        "text": """Following the authorization of the repair estimate, Premier Auto Body Shop Service Coordinator Rebecca Sullivan (Employee ID #RS-9921) initiated the logistical phase of the repair on January 19, 2024, at 08:30:00 hours. Sullivan accessed the Honda Interactive Network (HIN) to place a direct order with the Honda Parts Distribution Center (PDC) located in Portland, Oregon. The order was logged under Purchase Order PO-2024-0892. The requisition included 42 distinct line items required for the restoration of the 2022 Honda Accord (VIN ending in 3456). Key components ordered included the Front Subframe (Part #50200-TVA-A41), Left Front Fender (Part #60260-TVA-A00ZZ), and the Left Headlight Assembly. The total parts valuation was $12,450.00. Sullivan utilized the 'Critical Backorder' status to expedite shipping via FedEx Freight Priority. Inventory verification confirmed that 90% of the parts were in stock at the Portland facility. However, the Driver Side A-Pillar Reinforcement (Part #63100-TVA-305ZZ) was identified as out-of-stock regionally. Sullivan coordinated with the National Parts Warehouse in Marysville, Ohio, to drop-ship this structural component via overnight air cargo to ensure it arrived by January 22. This avoided a potential 4-day delay in the critical path of the repair. On the shop floor, Foreman Thomas Blake convened a pre-repair blueprinting session with Lead Technician Carlos Martinez (I-CAR Platinum Welder ID #W-8821). They reviewed the Honda Body Repair Manual (BRM) Section 4-2 regarding High-Strength Steel (HSS) welding parameters. They established that the A-pillar replacement would require squeeze-type resistance spot welding (STRSW) to replicate factory bond strength. Quality Control (QC) hold-points were established: QC-1 for Frame Alignment verification, QC-2 for Structural Weld inspection, and QC-3 for Paint Color Match. Sullivan updated the customer, Ms. Mitchell, via the automated CRM text system, providing a tracking link and a confirmed completion date of January 30, 2024. All procurement documents and tracking numbers (FedEx #7728-1192-9921) were scanned into the Repair Order digital jacket RO-2024-0892."""
    }
    
    # Page 10: Event 9 - Legal Documentation (type: Details)
    page10 = {
        "header": "Legal Documentation and Liability Determination",
        "date": "2024-01-18 13:30:00",
        "involved_parties": ["Seattle Police", "State Farm Insurance", "Progressive Legal Department"],
        "type": "Details",
        "text": """The legal disposition of the incident was formalized on January 18, 2024. Seattle Police issued Traffic Citation TC-2024-0891 to Mr. Robert Chen for violation of RCW 46.61.050 (Failure to Obey Traffic Control Device). The citation mandates an appearance at Seattle Municipal Court and carries a presumptive fine of $500.00 plus statutory assessments. Following this, State Farm Insurance (insuring Mr. Chen under Policy SF-AUTO-2847562) issued a Liability Acceptance Letter (Doc #SF-LA-2024) on January 18 at 13:30:00, signed by Claims Manager Jennifer Wu. They accepted 100% negligence, waiving all comparative fault defenses. Officer James Wilson documented the violation based on comprehensive evidence including municipal traffic camera footage showing the signal violation, security camera video from two commercial establishments, sworn witness testimony from Marcus Thompson, and Chen's own statement acknowledging he did not see the red signal. The complete evidence package was compiled in official police report SPD-2024-0156 with supplemental investigation report SPD-2024-0156-SUPP completed on January 17, 2024. Chen's insurance carrier State Farm Insurance was notified of the incident on January 15 at 16:45:00 hours through Chen's direct phone call to their claims department reporting the accident. State Farm assigned claim number SF-2024-WA-12847 and Claims Representative Michael Torres, a senior liability adjuster with 10 years experience handling complex collision claims, to investigate their insured's liability exposure and coordinate with all affected parties including Progressive Insurance, Mitchell, and Rodriguez. Torres contacted Progressive Insurance Claims Adjuster Linda Martinez on January 17 at 10:30:00 hours to discuss liability determination, damage assessment figures, and coordinated payment arrangements. Initial investigation by State Farm including review of police report, traffic camera footage, witness statements, and Chen's recorded statement confirmed their insured's fault based on comprehensive evidence clearly establishing red light violation as proximate cause of the collision with no contributing factors from other parties. The acceptance letter document SF-LA-2024-12847 confirms their responsibility for all damages sustained by Sarah Mitchell including vehicle property damage of $44,010, medical treatment expenses of $3,840, and any additional costs related to the collision incident. The letter explicitly waived any dispute of liability and confirmed no contributory negligence attributed to Mitchell based on all available evidence. No litigation anticipated given clear liability evidence and cooperative claims handling between insurance carriers following industry best practices and state insurance regulations."""
    }
    
    # Page 11: Event 10 - Subrogation Process (type: Details)
    page11 = {
        "header": "Subrogation Process and Recovery",
        "date": "2024-01-20 11:00:00",
        "involved_parties": ["Progressive Subrogation Department", "State Farm Insurance", "Finance Department"],
        "type": "Details",
        "text": """Progressive Auto Insurance Subrogation Department initiated formal subrogation recovery procedures on January 20, 2024, at 11:00:00 hours under direction of Subrogation Specialist David Chen, who manages the Pacific Northwest regional subrogation portfolio including Washington, Oregon, and Idaho claims with annual recovery amounts exceeding $12 million. The subrogation process seeks to recover all amounts paid by Progressive to Mitchell from the at-fault party's insurance carrier State Farm Insurance, thereby restoring Progressive's financial position and ultimately recovering Mitchell's $500 collision deductible to make her completely whole. Chen prepared comprehensive subrogation demand package under file number SUB-2024-00789 containing complete documentation of all payments, liability evidence, and legal basis for recovery under Washington state insurance law and contractual subrogation rights. The subrogation demand package included itemized statement of damages totaling $47,850, copies of all paid invoices and receipts with proof of payment via electronic funds transfer, certified copy of police report SPD-2024-0156 establishing Chen's fault and traffic violation, traffic camera video footage and forensic analysis report VFA-2024-0156, sworn witness statement from Marcus Thompson document WT-2024-0156-001, State Farm's liability acceptance letter document SF-LA-2024-12847 acknowledging 100 percent fault, and legal memorandum from attorney Patricia Anderson establishing clear liability under Washington negligence law and Progressive's subrogation rights under RCW 48.18.540. Chen transmitted the subrogation demand to State Farm Insurance Subrogation Department via certified mail with return receipt requested on January 20, 2024, and simultaneously sent electronic copy via the E-Subro Hub portal (Trans ID #ESH-99281) to State Farm Subrogation Manager Robert Williams at their regional office in Portland, Oregon. The demand letter cited the Inter-Company Arbitration Agreement conventions, requiring payment within 30 days. Chen included detailed breakdown showing Progressive's total payout of $47,850 plus Mitchell's $500 deductible for combined subrogation demand of $48,350. State Farm Insurance responded to the subrogation demand on January 23, 2024, with acknowledgment letter from Subrogation Manager Robert Williams confirming receipt of demand package and accepting full liability for reimbursement without dispute or reservation of rights. Williams stated that State Farm would process the subrogation payment in two installments: first payment of $40,000 to be issued February 1, 2024, and second payment of $8,350 to be issued February 15, 2024, due to internal payment authorization procedures requiring dual approval for amounts exceeding $40,000. This successful subrogation ensures that Progressive's loss ratio is unaffected and, crucially, that Ms. Mitchell will receive her $500.00 deductible refund check (Check #SUB-REF-221) by February 5, 2024."""
    }
    
    # Page 12: Event 11 - Claim Finalization (type: Details)
    page12 = {
        "header": "Repair Completion and Quality Assurance",
        "date": "2024-01-30 14:00:00",
        "involved_parties": ["Premier Auto Body Shop", "Progressive Insurance", "Sarah Mitchell"],
        "type": "Details",
        "text": """The restoration of the 2022 Honda Accord was concluded on January 30, 2024, at 14:00:00 hours, adhering strictly to the 18-day timeline. The Final Quality Assurance (QA) process was rigorous. Shop Foreman Thomas Blake utilized the Hunter Engineering frame measurement system one final time to generate a 'Post-Repair Scan'. The report confirmed that all control points on the unibody were within 2 millimeters of factory tolerance, verifying the structural integrity of the replaced subframe and A-pillar. The welding zones were inspected visually and via dye penetrant testing to ensure zero porosity. The paint finish was audited using a DeFelsko PosiTector 6000 coating thickness gage and a gloss meter; readings averaged 85 Gloss Units (GU), indistinguishable from the factory finish. Mechanics verified the suspension torque specs: the subframe bolts were torqued to exactly 85 ft-lbs, and wheel lugs to 80 ft-lbs. Progressive Field Inspector Monica Rodriguez arrived at 16:00:00 to perform the insurance validation. She conducted a 5-mile road test to check for wind noise, alignment drift, and suspension rattles. The vehicle passed all checkpoints. Rodriguez signed the Certificate of Repair Satisfaction (Doc #CRS-9921) and authorized the release of the final payment. Premier Auto Body issued a Lifetime Warranty (Cert #WAR-2024-0156) covering the workmanship for the duration of Ms. Mitchell's ownership. Ms. Mitchell was notified at 17:00:00 via phone. She arrived the following morning, January 31, at 09:00:00. After a walk-around inspection where she verified the paint match and door gaps, she signed the Vehicle Release Form. She returned the Enterprise rental vehicle (VIN ending 9921) to the agency branch at 09:45:00. The final rental invoice was closed at $1,170.00, billing directly to Progressive. Mitchell expressed complete satisfaction with the repair quality, paint finish, and overall appearance of her vehicle, rating the entire claims experience as excellent in the customer satisfaction survey completed on February 5, 2024."""
    }
    
    # Page 13: Overview - Final Summary (type: Overview)
    page13 = {
        "header": "Claim Resolution and Final Summary",
        "date": "2024-02-05",
        "involved_parties": ["Progressive Auto Insurance", "Sarah Mitchell", "Claims Department"],
        "type": "Overview",
        "text": """Claim CLM-2024-00789-AUTO was closed on February 5, 2024, by Regional Claims Manager David Thompson. The total processing time from First Notice of Loss on January 15 to final resolution was 21 calendar days, meeting industry standards. Senior Claims Adjuster Linda Martinez managed the claim with continuous communication to the policyholder. Total claim value: $47,850.00, comprising vehicle damage of $44,010.00 and medical expenses of $3,840.00. Mitchell received a net vehicle settlement of $43,510.00 via EFT on February 2, 2024, after her $500 deductible. All medical providers were paid directly on February 3, 2024, with zero out-of-pocket costs to the policyholder. Vehicle repairs were completed by Premier Auto Body Shop on January 30, 2024, restoring the 2022 Honda Accord to pre-accident condition with all structural repairs meeting Honda factory specifications. Mitchell completed her physical therapy program on February 1, 2024. Dr. Patterson issued full medical clearance on February 4, 2024, confirming complete recovery with no permanent injury. Subrogation recovery from State Farm Insurance is in progress, with Mitchell's $500 deductible refund processed on February 5, 2024. Claim status: CL-APPROVED-SETTLED. Customer satisfaction survey rating: 10/10."""
    }
    
    return [page1, page2, page3, page4, page5, page6, page7, page8, page9, page10, page11, page12, page13]


def generate_pdf(filename="insurance_claim.pdf"):
    """Generate the PDF document with proper formatting."""
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='darkblue',
        spaceAfter=12,
        spaceBefore=12
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=6
    )
    
    pages_content = create_claim_content()
    
    for i, page_content in enumerate(pages_content):
        if i == 0:
            story.append(Paragraph("INSURANCE CLAIM DOCUMENT", title_style))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(page_content["header"], header_style))
        story.append(Spacer(1, 0.1*inch))
        
        paragraphs = page_content["text"].split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 0.1*inch))
        
        if i < len(pages_content) - 1:
            story.append(PageBreak())
    
    doc.build(story)
    print(f"[OK] PDF generated: {filename}")
    
    return pages_content


def generate_metadata(pages_content, filename="claim_metadata.json"):
    """Generate metadata JSON file."""
    
    metadata = {}
    
    for i, page_content in enumerate(pages_content, start=1):
        metadata[f"page_{i}"] = {
            "page_number": i,
            "header": page_content["header"],
            "involved_parties": page_content["involved_parties"],
            "date": page_content["date"],
            "type": page_content["type"],
            "character_count": len(page_content["text"])
        }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Metadata generated: {filename}")
    return metadata


def main():
    """Main execution function."""
    print("=" * 70)
    print("Insurance Claim PDF Generator - 13 Pages")
    print("=" * 70)
    print()
    
    print("Generating 13-page PDF document...")
    pages_content = generate_pdf("insurance_claim.pdf")
    print()
    
    print("Generating metadata...")
    metadata = generate_metadata(pages_content, "claim_metadata.json")
    print()
    
    print("=" * 70)
    print("GENERATION SUMMARY")
    print("=" * 70)
    print(f"Total pages: {len(pages_content)}")
    print()
    print("Character counts per page:")
    for page_num, page_data in metadata.items():
        page_type = " (OVERVIEW)" if page_data['type'] == 'Overview' else ""
        print(f"  {page_num}: {page_data['character_count']} characters{page_type}")
    print()
    
    overview_pages = [p for p in metadata.values() if p['type'] == 'Overview']
    details_pages = [p for p in metadata.values() if p['type'] == 'Details']
    print(f"Overview pages: {len(overview_pages)}")
    print(f"Details pages: {len(details_pages)}")
    print()
    
    chunk_size = 400
    overlap = 50
    print("Chunking Analysis:")
    print(f"  Chunk size: {chunk_size} characters")
    print(f"  Overlap: {overlap} characters")
    print()
    total_chunks = 0
    for page_num, page_data in metadata.items():
        chars = page_data['character_count']
        effective_step = chunk_size - overlap
        num_chunks = ((chars - chunk_size) // effective_step) + 1 if chars >= chunk_size else 1
        total_chunks += num_chunks
        print(f"  {page_num}: ~{num_chunks} chunks")
    print()
    print(f"Total estimated chunks: ~{total_chunks}")
    print()
    
    print("[OK] All files generated successfully!")
    print()
    print("Output files:")
    print("  - insurance_claim.pdf (13 pages)")
    print("  - claim_metadata.json (13 pages)")
    print()
    print("Next steps:")
    print("  1. Review the generated PDF and metadata")
    print("  2. Run indexing to create chunks and summaries")
    print("  3. Test with query system")
    print("=" * 70)


if __name__ == "__main__":
    main()
