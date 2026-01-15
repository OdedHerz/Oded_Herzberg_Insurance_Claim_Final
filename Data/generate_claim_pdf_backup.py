"""
Insurance Claim PDF Generator - 13 Pages
Generates a comprehensive synthetic insurance claim document with timeline-based events.
Each page contains ~1800-1900 characters for optimal hierarchical chunking (5 chunks per page).
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
    
    # Page 1: Introduction (~1800 chars with paragraph breaks every ~400 chars)
    intro_content = {
        "header": "Claim Introduction and Overview",
        "date": "2024-01-15",
        "involved_parties": ["Sarah Mitchell", "Progressive Auto Insurance", "Claims Department"],
        "type": "Overview",
        "text": """This insurance claim is filed under claim number CLM-2024-00789-AUTO and policy number PAI-8847562-2023. The claim was officially submitted on January 15, 2024, at 14:32:17 hours through Progressive Auto Insurance and will be processed according to standard company procedures.

The policyholder is Sarah Mitchell, a 34-year-old software engineer residing at 4582 Birch Lane, Seattle, Washington 98102, who holds a Comprehensive Auto Insurance policy covering her 2022 Honda Accord with vehicle identification number 1HGCV1F3XNA123456. The policy was initiated on March 15, 2023, and includes coverage of $500,000 for liability claims, $100,000 for collision damage to the insured vehicle, $50,000 for uninsured motorist protection, and comprehensive medical payments coverage up to $25,000 per incident.

A multi-vehicle collision occurred on January 15, 2024, at 09:23:45 AM at the intersection of Maple Avenue and 5th Street in Downtown Seattle, Washington, postal code 98101. The incident involved three vehicles total: the insured Honda Accord, a 2019 Toyota Camry driven by Robert Chen, and a parked 2020 Ford F-150 pickup truck. The collision resulted in significant property damage to all three vehicles and minor personal injuries requiring immediate medical attention, emergency response team deployment, and subsequent police investigation.

Initial damage assessment conducted by certified insurance adjusters estimates the total claim value at $47,850 dollars including vehicle repairs of $44,010 and medical expenses of $3,840. The incident occurred during morning rush hour traffic conditions with wet road surfaces from overnight rainfall that accumulated to 0.3 inches. Ambient temperature was recorded at 42 degrees Fahrenheit with wind speeds of 8 miles per hour from the southwest. All involved parties have provided official statements to investigating officers, and multiple independent witnesses have corroborated the sequence of events. Traffic signal camera footage and dashboard camera recordings from Mitchell's vehicle provide conclusive evidence of the collision circumstances and liability determination."""
    }
    
    # Page 2: Initial Incident Event (~1850 chars)
    event1_content = {
        "header": "Event 1: Initial Collision",
        "date": "2024-01-15 09:23:45",
        "involved_parties": ["Sarah Mitchell", "Robert Chen", "Seattle Police Department", "Officer James Wilson"],
        "type": "Details",
        "text": """The collision occurred on January 15, 2024, at exactly 09:23:45 AM at the intersection of Maple Avenue and 5th Street in Seattle, Washington, zip code 98101. GPS coordinates recorded at the scene were 47.6062 degrees North latitude and 122.3321 degrees West longitude for precise location documentation. The intersection is classified as a major urban traffic control point with average daily traffic volume of 28,500 vehicles and is equipped with advanced traffic monitoring systems including high-definition cameras positioned at all four corners of the intersection.

Policyholder Sarah Mitchell was traveling northbound on Maple Avenue at approximately 25 miles per hour in moderate traffic. Weather conditions included light rain with 0.3 inches precipitation, temperature at 42 degrees Fahrenheit, and visibility reduced to 200 feet. The traffic signal was displaying green for northbound traffic.

At 09:23:45 hours, a 2019 Toyota Camry bearing license plate WA-ABC-1234 driven by Robert Chen entered the intersection traveling eastbound at 45 mph in a posted 30 mph zone. Security camera footage shows Chen's vehicle entering against a red traffic signal that had been active for 2.3 seconds.

The collision impact occurred on the driver's side front quarter panel causing significant structural damage including door frame deformation and fender crushing. Impact force caused Mitchell's vehicle to rotate counterclockwise 45 degrees and collide with a parked 2020 Ford F-150 owned by James Rodriguez. Vehicle airbags deployed at 09:23:46. Mitchell reported neck pain rated 6 out of 10, dizziness, and disorientation."""
    }
    
    # Page 3: Emergency Response Event (~1850 chars)
    event2_content = {
        "header": "Event 2: Emergency Response and Assessment",
        "date": "2024-01-15 09:31:22",
        "involved_parties": ["Seattle Fire Department", "Medic Unit 47", "Paramedic Jennifer Ross", "Officer James Wilson", "Sarah Mitchell"],
        "type": "Details",
        "text": """First responders arrived at 09:31:22 AM, a response time of 7 minutes 37 seconds. Response units included Seattle Fire Engine 10, Medic Unit 47, and Police Unit 3-Adam-12. Paramedic Jennifer Ross immediately assessed Mitchell's medical condition following standard triage protocols.

Vital signs showed blood pressure 145/92, heart rate 98 bpm, respiratory rate 18 breaths/min, and oxygen saturation 98%. Mitchell was alert and oriented, scoring 15/15 on Glasgow Coma Scale. She complained of neck stiffness, headache severity 6/10, and cervical spine tenderness between C3-C6.

Officer Wilson secured the intersection at 09:32:00 and established a perimeter. Photographic evidence showed skid marks measuring 47 feet from Chen's vehicle. Traffic camera footage confirmed Chen entered 2.3 seconds after the light turned red, violating RCW 46.61.050.

Chen's vehicle maintenance records showed a brake warning light active for 12 days, documented under ticket BRK-2024-0103. Property damage estimates: Mitchell vehicle $18,400, Chen vehicle $22,300, F-150 $7,150, total $47,850."""
    }
    
    # Page 4: Investigation and Medical Follow-up (~1850 chars)
    event3_content = {
        "header": "Event 3: Investigation and Medical Documentation",
        "date": "2024-01-15 14:45:18",
        "involved_parties": ["Dr. Michael Patterson", "Sarah Mitchell", "Claims Adjuster Linda Martinez", "Police Investigation Unit"],
        "type": "Details",
        "text": """Mitchell was transported to Seattle Medical Center, arriving at 10:15:33 AM. She was examined by Dr. Michael Patterson at 14:45:18 after triage. Diagnosis: Grade 2 whiplash injury, cervical spine strain C3-C6, and mild concussion with headache and dizziness.

CT scan at 15:23:00 showed no structural damage to cervical spine or brain. Treatment plan: 12 physical therapy sessions over six weeks, Ibuprofen 600mg three times daily, Cyclobenzaprine 10mg at bedtime, and soft cervical collar for two weeks.

Claims Adjuster Linda Martinez interviewed Mitchell at 16:30:00 to document incident details. Mitchell provided dashboard camera footage showing her vehicle at 24 mph, green signal, and Chen's vehicle entering at high speed. Police report SPD-2024-0156 filed at 17:15:00 with complete documentation.

Total claim value $47,850: vehicle damage $44,010 and medical expenses $3,840. Liability assigns 100% fault to Chen based on traffic signal evidence, witness statements, and police citation. Claim approved at 18:22:33 with 15-20 business day resolution and rental authorization."""
    }
    
    # Page 5: Vehicle Inspection & Repair Assessment (~1850 chars)
    event4_content = {
        "header": "Event 4: Vehicle Inspection and Repair Assessment",
        "date": "2024-01-16 10:30:00",
        "involved_parties": ["Premier Auto Body Shop", "Certified Inspector Thomas Blake", "Sarah Mitchell", "Progressive Insurance Adjuster"],
        "type": "Details",
        "text": """Mitchell's 2022 Honda Accord was transported to Premier Auto Body Shop on January 16, 2024, at 10:30:00 AM for damage assessment. Inspector Thomas Blake, an ASE Master Certified technician, conducted examination using computerized diagnostic equipment and manual inspection protocols.

The inspection revealed extensive structural damage to the driver side A-pillar with 3.2 inches inward deformation, B-pillar reinforcement bracket with stress fractures, and front subframe showing 1.8 inches lateral displacement requiring complete replacement. Left front suspension components including control arm, tie rod end, and wheel bearing sustained impact damage. Additional damage: driver side door, front fender, hood, and headlight assembly. Total parts cost $12,450.

Labor estimates: 87.5 hours at $95/hour totaling $8,312.50. Additional costs: frame straightening $890, paint and color matching $2,340, wheel alignment $185, safety inspection $125. Complete repair timeline 14-18 business days.

Third-party appraiser David Richardson reviewed damage assessment on January 16 at 15:45:00. Richardson verified estimates and confirmed vehicle structural integrity can be restored. His report IAA-2024-1567 supported the $23,102.50 total repair cost."""
    }
    
    # Page 6: Medical Follow-up & Physical Therapy (~1850 chars)
    event5_content = {
        "header": "Event 5: Medical Follow-up and Physical Therapy",
        "date": "2024-01-22 08:00:00",
        "involved_parties": ["Dr. Michael Patterson", "Sarah Mitchell", "Physical Therapist Amanda Chen", "Seattle Rehabilitation Center"],
        "type": "Details",
        "text": """Mitchell attended her scheduled follow-up appointment with Dr. Michael Patterson at Seattle Medical Center Emergency Medicine Clinic on January 22, 2024, at 08:00:00 AM, exactly one week after the initial collision incident. The comprehensive examination revealed continued cervical spine tenderness with restricted range of motion measured at 45 degrees rotation to the right and 42 degrees to the left compared to normal baseline range of 80 degrees, flexion limited to 35 degrees versus normal 50 degrees, and extension limited to 40 degrees versus normal 60 degrees. Pain level reported decreased from initial six out of ten to current four out of ten on the numeric rating scale, indicating positive response to initial treatment and natural healing progression. Dr. Patterson performed manual palpation revealing tender points at C3-C4 and C5-C6 vertebral levels, assessed deep tendon reflexes finding normal responses bilaterally, and tested upper extremity strength showing 5 out of 5 power in all muscle groups indicating no nerve root impingement.

Dr. Patterson prescribed a comprehensive physical therapy program consisting of 12 sessions over six weeks at Seattle Rehabilitation Center, a state-licensed outpatient therapy facility specializing in orthopedic and spine rehabilitation. The detailed treatment plan includes therapeutic exercises for cervical spine mobility and strength, soft tissue massage therapy using myofascial release techniques, electrical stimulation therapy using transcutaneous electrical nerve stimulation TENS unit for pain management, ultrasound therapy for deep tissue healing, heat therapy using moist heat packs, and postural correction training with ergonomic workplace assessment. Mitchell was cleared to return to work on modified duty with medical restrictions limiting heavy lifting to maximum 10 pounds, avoiding overhead reaching activities, and allowing frequent position changes with breaks every 30 minutes to prevent prolonged static neck positioning.

Physical Therapist Amanda Chen, a licensed physical therapist with Doctor of Physical Therapy degree and certification in manual therapy and orthopedic physical therapy, conducted the initial therapy session on January 22 at 14:30:00 hours at Seattle Rehabilitation Center. The comprehensive 60-minute session included baseline mobility assessment using goniometric measurements, functional outcome questionnaire completion scoring 28 out of 50 on the Neck Disability Index indicating moderate disability, gentle stretching exercises for cervical paraspinal muscles, heat therapy application for 15 minutes using hydrocollator packs at 165 degrees Fahrenheit, and detailed patient education on proper posture, body mechanics, sleeping positions, and home exercise routine consisting of five exercises to be performed twice daily.

Progress notes documented in patient chart number PT-2024-0892 indicate good prognosis for full recovery within the six-week treatment window based on patient age, absence of prior neck injuries, motivated participation level, and positive response to initial interventions. Follow-up sessions scheduled for Mondays, Wednesdays, and Fridays at 14:30:00 hours with plan to progress exercises as tolerated. Total estimated medical treatment costs including physician follow-ups at $625, physical therapy sessions at $1,140, and medications at $185 calculated at $3,840 dollars, fully covered under Mitchell's comprehensive insurance policy medical payments benefits with zero copayment required."""
    }
    
    # Page 8: Additional Medical Evaluations (~2000 chars)
    event5_5_content = {
        "header": "Event 5.5: Additional Medical Evaluations and Imaging",
        "date": "2024-01-25 10:00:00",
        "involved_parties": ["Dr. Rebecca Santos", "Sarah Mitchell", "Seattle Radiology Associates", "Orthopedic Specialist"],
        "type": "Details",
        "text": """Mitchell underwent additional specialized medical evaluation with Dr. Rebecca Santos, a board-certified orthopedic surgeon specializing in spine and neck injuries, on January 25, 2024, at 10:00:00 AM at Seattle Orthopedic Associates clinic located at 3400 Medical Plaza Drive. The consultation was requested by Dr. Patterson to obtain specialist assessment of the cervical spine injury and ensure no underlying structural damage was overlooked in the initial emergency department evaluation. Dr. Santos conducted a comprehensive 45-minute examination including detailed neurological assessment, range of motion testing using standardized measurement protocols, provocative testing with Spurling's test and shoulder abduction relief sign, and review of all previous medical records and imaging studies.

Dr. Santos ordered additional diagnostic imaging including cervical spine MRI scan without contrast to evaluate soft tissue structures not visible on CT scan, specifically assessing intervertebral discs, spinal ligaments, nerve roots, and spinal cord integrity. The MRI examination was performed at Seattle Radiology Associates on January 25 at 14:30:00 hours using a Philips Ingenia 3.0 Tesla MRI scanner providing high-resolution imaging. The radiologist report completed by Dr. James Morrison indicated mild disc bulging at C4-C5 level without nerve root compression, anterior longitudinal ligament strain without rupture, mild soft tissue edema in the paraspinal muscles, and no evidence of herniated disc, spinal stenosis, or cord compression. These findings were consistent with Grade 2 whiplash injury and supported the current treatment plan without need for surgical intervention.

Dr. Santos also performed nerve conduction velocity studies to assess for any peripheral nerve damage affecting the upper extremities. The electromyography EMG and nerve conduction study NCS performed at 15:45:00 hours tested median nerve, ulnar nerve, and radial nerve function bilaterally. Results showed normal nerve conduction velocities, normal amplitude responses, and no evidence of nerve root impingement, brachial plexus injury, or peripheral neuropathy. These objective findings confirmed that Mitchell's symptoms were related to musculoskeletal injury without neurological complications.

Dr. Santos provided a comprehensive written report concluding that Mitchell sustained soft tissue cervical spine injury without structural damage, neurological deficit, or need for surgical intervention. The prognosis for complete recovery was rated as excellent with continuation of the prescribed physical therapy program. Dr. Santos recommended ongoing conservative treatment including physical therapy completion, anti-inflammatory medication as needed, and follow-up evaluation in four weeks to assess progress. The specialist report was forwarded to Dr. Patterson, Progressive Insurance medical review team, and documented in Mitchell's medical record under consultation note number ORTHO-2024-0234. The additional medical evaluation costs totaling $890 for the consultation, $1,250 for MRI imaging, and $650 for electrodiagnostic studies were pre-authorized by Progressive Insurance and covered under Mitchell's medical payments policy benefits."""
    }
    
    # Page 9: Witness Statement Documentation (~2000 chars)
    event6_content = {
        "header": "Witness Statement and Traffic Analysis",
        "date": "2024-01-15 11:45:00",
        "involved_parties": ["Marcus Thompson", "Seattle Police Department", "Traffic Engineer Dr. Susan Miller", "Video Forensics Team"],
        "type": "Details",
        "text": """Witness Marcus Thompson, a 42-year-old accountant employed by Seattle Financial Services residing at 1247 Oak Street, provided a detailed sworn statement to Seattle Police Department at 11:45:00 AM on January 15, 2024. Thompson, who was waiting at the Metro bus stop located at the southeast corner of the intersection of Maple Avenue and 5th Street, had an unobstructed view of the collision from approximately 35 feet away. His statement confirmed he observed Chen's vehicle approaching at high speed estimated at 40-50 miles per hour and entering the intersection against a red traffic signal. Thompson stated he was looking at his phone checking the time at 09:23:40 when he heard the sound of squealing tires, looked up, and witnessed the entire collision sequence.

Thompson's testimony included specific detailed observations: he noticed Chen's brake lights did not illuminate until after the vehicle had already entered the intersection indicating delayed reaction, the traffic signal had been red for approximately two to three seconds before Chen's vehicle entered based on his observation of the light change, Mitchell's vehicle had already proceeded partially through the intersection with right of way, and he immediately called 911 emergency services at 09:24:33 providing his contact information and offering to remain at the scene as a witness. His statement was recorded by Officer Wilson as official witness testimony document number WT-2024-0156-001 with Thompson signing the statement under penalty of perjury attesting to its accuracy. Thompson also provided his business card with contact information for follow-up interviews and expressed willingness to testify in court if required.

Traffic Engineer Dr. Susan Miller from Seattle Department of Transportation Traffic Operations Division conducted a comprehensive analysis of the intersection traffic signal timing, signal equipment functionality, and road surface conditions on January 16, 2024. Her detailed engineering report documented that the traffic signal operates on a standard 90-second cycle with 35 seconds green phase for northbound traffic, 5 seconds yellow clearance interval, 3 seconds all-red clearance phase for safety, 35 seconds green for eastbound traffic, and repeated cycle pattern. Signal maintenance records retrieved from the automated monitoring system confirmed the system was functioning correctly with all timing parameters within specifications and the most recent preventive maintenance inspection completed on January 10, 2024, by certified traffic signal technician Michael Rodriguez.

The Video Forensics Team from Seattle Police Department Technical Services Division analyzed footage from three different security cameras covering the intersection including the municipal traffic camera, First National Bank exterior security camera, and Corner Cafe surveillance system. Frame-by-frame analysis using specialized video forensic software confirmed Chen's vehicle entered the intersection at timestamp 09:23:45.127 while the traffic signal had transitioned to red at timestamp 09:23:42.850, providing definitive evidence supporting a 2.277 second red light violation. The forensic video analysis report completed by Detective Sarah Kim was filed as evidence document VFA-2024-0156 with digital copies of all video footage preserved on encrypted storage media."""
    }
    
    # Page 9: Financial Breakdown & Policy Coverage (~1850 chars)
    event7_content = {
        "header": "Financial Breakdown and Insurance Coverage",
        "date": "2024-01-17 09:00:00",
        "involved_parties": ["Progressive Auto Insurance", "Claims Adjuster Linda Martinez", "Sarah Mitchell", "Finance Department"],
        "type": "Details",
        "text": """Progressive Auto Insurance Claims Adjuster Linda Martinez completed the comprehensive financial assessment and cost breakdown analysis on January 17, 2024, at 09:00:00 AM in coordination with the Progressive Insurance Finance Department Claims Payment Division. The detailed itemized breakdown enumerates all costs associated with the claim under file number CLM-2024-00789-AUTO with supporting documentation, receipts, and cost verification for each line item. Mitchell's policy number PAI-8847562-2023 provides comprehensive auto insurance coverage with a $500 deductible for collision claims, $100,000 maximum coverage limit per incident for property damage, $500,000 liability coverage for third-party claims, and $25,000 medical payments coverage for injury treatment expenses.

Vehicle damage costs totaling $44,010 include Premier Auto Body Shop repair estimate of $23,102.50, rental vehicle expenses for 18 days at $65 per day equaling $1,170, towing and storage fees of $485, diminished value assessment of $18,400, and administrative processing fees of $852.50. The rental vehicle authorization extends through the estimated repair completion date with direct billing arrangement with Enterprise Rent-A-Car.

Medical expenses documented at $3,840 include emergency department treatment at $1,250, CT scan and diagnostic imaging at $890, physician consultations at $625, physical therapy program of 12 sessions totaling $1,140, prescription medications at $185, and medical records fees at $50. All medical costs were pre-authorized and payable directly to healthcare providers with zero out-of-pocket cost to Mitchell.

Total claim value of $47,850 falls well within policy coverage limits providing adequate financial protection for all accident-related expenses. Mitchell's $500 collision deductible applies to the vehicle damage portion only as specified in policy section 4.2.1, resulting in net payment to Mitchell of $43,510 for vehicle-related costs including repairs, rental, towing, and diminished value, and $3,840 paid directly to medical providers for all treatment expenses. Claims processing timeline estimated at 15 to 20 business days from claim approval with electronic funds transfer initiated upon completion of all required documentation, verification procedures, and claims authorization signatures. Payment distribution scheduled with vehicle repair payment issued February 2, 2024, and medical payments processed February 3, 2024."""
    }
    
    # Page 10: Repair Shop Coordination (~1850 chars)
    event7_5_content = {
        "header": "Event 7.5: Repair Shop Coordination and Parts Procurement",
        "date": "2024-01-19 08:30:00",
        "involved_parties": ["Premier Auto Body Shop", "Thomas Blake", "Honda Parts Department", "Sarah Mitchell"],
        "type": "Details",
        "text": """Premier Auto Body Shop Service Coordinator Rebecca Sullivan initiated comprehensive repair coordination procedures on January 19, 2024, at 08:30:00 hours following receipt of insurance authorization and approval to proceed with repairs on Mitchell's 2022 Honda Accord. Sullivan contacted Honda Parts Distribution Center in Portland, Oregon, to order all required original equipment manufacturer parts identified in the repair estimate including structural components, body panels, suspension parts, and trim pieces. The parts order was placed under purchase order number PO-2024-0892 with total parts value of $12,450 and requested delivery date of January 23, 2024.

The parts procurement process included verification of vehicle identification number 1HGCV1F3XNA123456 to ensure correct part fitment and confirmation of paint code NH-883P for Platinum White Pearl color matching. Sullivan confirmed that most required parts were in stock at the regional distribution center including the front subframe assembly, control arm, tie rod end, and body panels. However, the driver side A-pillar reinforcement required special order from Honda's national parts warehouse in Ohio with estimated arrival at the regional center on January 22, 2024.

Shop Foreman Thomas Blake conducted a pre-repair planning meeting with the assigned technician Carlos Martinez, an ASE Master Certified technician with I-CAR Platinum welding certification, to review repair procedures and establish quality control checkpoints throughout the repair process. The planning session addressed the frame straightening procedure using the Hunter computerized frame measurement system, structural welding requirements following Honda's certified repair procedures for high-strength steel components, and final quality inspection protocols. Blake also coordinated with the paint department to schedule color matching and application of the multi-stage pearl paint system.

Sullivan maintained regular communication with Mitchell providing repair status updates via text message and email. On January 19, Sullivan sent Mitchell a detailed timeline showing parts order placement, expected parts arrival dates, repair milestone schedule, and estimated completion date of January 30, 2024. Mitchell was reminded that her rental vehicle authorization remained active through repair completion and that she would receive notification 24 hours before her vehicle would be ready for pickup. The repair coordination documentation was maintained in shop file RO-2024-0892 with digital copies uploaded to Progressive Insurance's claim management portal for real-time tracking and verification purposes."""
    }
    
    # Page 11: Legal & Liability Documentation (~1850 chars)
    event8_content = {
        "header": "Legal Documentation and Liability Determination",
        "date": "2024-01-18 13:30:00",
        "involved_parties": ["Seattle Police Department", "Officer James Wilson", "Robert Chen", "Chen's Insurance - State Farm", "Legal Department"],
        "type": "Details",
        "text": """Seattle Police Department issued official traffic citation TC-2024-0891 to Robert Chen on January 18, 2024, for violation of RCW 46.61.050 for failure to obey a traffic control device. The citation carries mandatory court appearance, base fine of $500 plus court costs of $185, and four penalty points on driving record. Officer Wilson documented the violation based on traffic camera footage, security camera video, witness testimony, and Chen's statement. The evidence package was compiled in police report SPD-2024-0156.

Chen's insurance carrier State Farm was notified on January 15 at 16:45:00 hours. State Farm assigned claim SF-2024-WA-12847 and Claims Representative Michael Torres to investigate liability. Torres contacted Progressive's Linda Martinez on January 17 to discuss liability, damage assessment, and subrogation. Initial investigation confirmed their insured's fault based on comprehensive evidence establishing red light violation as proximate cause.

State Farm issued formal liability acceptance letter on January 18, 2024, at 13:30:00 acknowledging 100 percent fault on behalf of Robert Chen under policy SF-AUTO-2847562-2023. The acceptance letter SF-LA-2024-12847 confirms responsibility for all damages including vehicle damage of $44,010, medical expenses of $3,840, and lost wages totaling $675. No litigation anticipated given clear liability evidence and cooperative claims handling.

Progressive Legal Department reviewed all documentation on January 18, 2024. Legal counsel Patricia Anderson issued clearance memorandum LA-2024-0156 authorizing claims payment and initiating subrogation recovery. The subrogation demand was filed with State Farm under file SUB-2024-00789 to recover all costs including Mitchell's $500 deductible. State Farm acknowledged the demand and agreed to full reimbursement with payment scheduled for March 1, 2024."""
    }
    
    # Page 12: Subrogation Process Initiation (~1850 chars)
    event8_5_content = {
        "header": "Event 8.5: Subrogation Process and Inter-Insurance Coordination",
        "date": "2024-01-20 11:00:00",
        "involved_parties": ["Progressive Subrogation Department", "State Farm Insurance", "Legal Team", "Finance Department"],
        "type": "Details",
        "text": """Progressive Auto Insurance Subrogation Department initiated formal subrogation recovery procedures on January 20, 2024, at 11:00:00 hours under the direction of Subrogation Specialist David Chen, who manages the Pacific Northwest regional subrogation portfolio including Washington, Oregon, and Idaho claims. The subrogation process seeks to recover all amounts paid by Progressive to Mitchell from the at-fault party's insurance carrier State Farm Insurance, thereby restoring Progressive's financial position and ultimately recovering Mitchell's $500 collision deductible to make her completely whole. Chen prepared a comprehensive subrogation demand package under file number SUB-2024-00789 containing complete documentation of all payments, liability evidence, and legal basis for recovery.

The subrogation demand package included itemized statement of damages totaling $47,850, copies of all paid invoices and receipts, certified copy of police report SPD-2024-0156, traffic camera footage and forensic analysis report VFA-2024-0156, witness statement from Marcus Thompson, State Farm's liability acceptance letter, and legal memorandum establishing Progressive's subrogation rights under Washington state law.

Chen transmitted the subrogation demand to State Farm Insurance via certified mail on January 20, 2024, with electronic copy sent to Subrogation Manager Robert Williams. The demand letter specified payment due date of February 20, 2024, and outlined consequences of non-payment including potential litigation and interest charges at 12 percent per annum. The demand totaled $48,350 including Progressive's payout and Mitchell's deductible.

State Farm Insurance responded on January 23, 2024, confirming receipt and accepting full liability for reimbursement. State Farm agreed to process payment in two installments: $40,000 on February 1, 2024, and $8,350 on February 15, 2024. Progressive accepted this arrangement with agreement documented in settlement memorandum SS-2024-00789. Mitchell's $500 deductible would be refunded upon receipt of the first payment, scheduled for February 5, 2024. Regular status updates were provided to Mitchell explaining the recovery process."""
    }
    
    # Page 13: Claim Resolution Summary (type: Overview) (~1850 chars)
    event9_content = {
        "header": "Claim Resolution and Final Summary",
        "date": "2024-02-05",
        "involved_parties": ["Progressive Auto Insurance", "Sarah Mitchell", "Claims Department", "Finance Department"],
        "type": "Overview",
        "text": """Final claim resolution completed on February 5, 2024, for claim number CLM-2024-00789-AUTO under policy PAI-8847562-2023 for policyholder Sarah Mitchell. All documentation reviewed and approved by Progressive Auto Insurance Claims Department with final authorization from Regional Claims Manager David Thompson. Total processing time from initial filing on January 15, 2024, to final resolution on February 5, 2024, was 21 calendar days meeting Progressive's service standards of 15 to 25 business days for collision claims with clear liability. The claim was managed by Senior Claims Adjuster Linda Martinez who maintained excellent communication with Mitchell throughout the entire process.

Total claim payout amount of $47,850 distributed as follows: vehicle damage settlement of $43,510 representing net amount after Mitchell's $500 collision deductible paid to Sarah Mitchell via electronic funds transfer on February 2, 2024, transaction reference number EFT-2024-02-00789 deposited directly to her checking account. Medical expenses totaling $3,840 paid directly to healthcare providers including $2,765 to Seattle Medical Center and $1,075 to Seattle Rehabilitation Center on February 3, 2024, ensuring zero out-of-pocket medical costs for Mitchell. Mitchell's $500 collision deductible scheduled to be recovered through subrogation from State Farm Insurance.

Vehicle repairs completed by Premier Auto Body Shop on January 30, 2024, with comprehensive final inspection approval documented under quality control certificate QCC-2024-0156. Mitchell's vehicle returned to pre-accident condition with all structural repairs meeting Honda factory specifications and computerized frame measurements confirming proper alignment within 2 millimeters. Premier Auto Body Shop provided lifetime warranty on all structural and collision repairs. Mitchell completed her 12-session physical therapy program on February 1, 2024, with Dr. Patterson issuing full medical clearance confirming complete recovery with no permanent injury anticipated.

Claim file officially closed on February 5, 2024, at 16:30:00 hours with final status code CL-APPROVED-SETTLED. All parties including Mitchell, Premier Auto Body Shop, healthcare providers, and third-party claimant James Rodriguez expressed satisfaction with claim resolution. No appeals or disputes filed. Customer satisfaction survey completed by Mitchell rating overall experience as excellent with five-star rating and positive comments praising Linda Martinez's professionalism. Subrogation recovery in progress with State Farm Insurance with first payment of $40,000 received February 1, 2024, and second payment of $8,350 scheduled for February 15, 2024."""
    }
    
    return [intro_content, event1_content, event2_content, event3_content, event4_content, 
            event5_content, event5_5_content, event6_content,
            event7_content, event7_5_content, event8_content, event8_5_content, event9_content]


def generate_pdf(filename="insurance_claim.pdf"):
    """Generate the PDF document with proper formatting."""
    
    # Create PDF document
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Container for the 'Flowable' objects
    story = []
    
    # Define styles
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
    
    # Get content
    pages_content = create_claim_content()
    
    # Build document
    for i, page_content in enumerate(pages_content):
        if i == 0:
            # Title page
            story.append(Paragraph("INSURANCE CLAIM DOCUMENT", title_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Add header
        story.append(Paragraph(page_content["header"], header_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Add body text - split into paragraphs for better readability
        paragraphs = page_content["text"].split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 0.1*inch))
        
        # Add page break except for last page
        if i < len(pages_content) - 1:
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    print(f"[OK] PDF generated: {filename}")
    
    # Return content for metadata generation
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
    
    # Generate PDF
    print("Generating 13-page PDF document...")
    pages_content = generate_pdf("insurance_claim.pdf")
    print()
    
    # Generate metadata
    print("Generating metadata...")
    metadata = generate_metadata(pages_content, "claim_metadata.json")
    print()
    
    # Display summary
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
    
    # Count Overview and Details pages
    overview_pages = [p for p in metadata.values() if p['type'] == 'Overview']
    details_pages = [p for p in metadata.values() if p['type'] == 'Details']
    print(f"Overview pages: {len(overview_pages)} (always included by Summary Agent)")
    print(f"Details pages: {len(details_pages)}")
    print()
    
    # Calculate chunking info
    chunk_size = 400
    overlap = 50
    print("Chunking Analysis:")
    print(f"  Chunk size: {chunk_size} characters")
    print(f"  Overlap: {overlap} characters")
    print()
    total_chunks = 0
    for page_num, page_data in metadata.items():
        chars = page_data['character_count']
        # Calculate approximate number of chunks
        # First chunk: 0-300, Second: 260-560, Third: 520-820, etc.
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

