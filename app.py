# import streamlit as st
# import smtplib
# import ssl
# from email.message import EmailMessage
# import dropbox
# from dotenv import load_dotenv
# import os
# import requests

# # ----------- LOAD SECRETS -----------
# load_dotenv()

# DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
# DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
# DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
# SENDER_EMAIL = os.getenv("SENDER_EMAIL")
# SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
# RECEIVER_EMAIL_SELF = os.getenv("RECEIVER_EMAIL_SELF")
# MAX_MB = 100

# # ----------- PAGE SETUP & STYLING -----------
# st.set_page_config(page_title="AIR Report Upload", layout="centered")

# st.markdown("""
#     <style>
#     body, .main {
#         background-color: #062f5f;
#         color: white;
#     }
#     .form-wrapper {
#         display: flex;
#         justify-content: center;
#         align-items: center;
#         padding: 2rem;
#     }
#     .form-card {
#         color: black !important;
#         padding: 2rem;
#         border-radius: 15px;
#         box-shadow: 0 4px 20px rgba(0,0,0,0.2);
#         max-width: 700px;
#         width: 100%;
#     }
#     .thin-line {
#         height: 1px;
#         background-color: white;
#         border: none;
#         margin-top: 10px;
#         margin-bottom: 20px;
#     }
#     .note {
#         background-color: white;
#         color: black;
#         padding: 1rem;
#         border-left: 6px solid #4CAF50;
#         border-radius: 8px;
#         margin-top: 1.5rem;
#     }
#     header, .block-container {
#         padding-top: 2rem !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # ----------- HEADER SECTION -----------
# st.image("assets/logo.png", width=120)
# st.markdown('<hr class="thin-line">', unsafe_allow_html=True)

# # ----------- FORM CENTERED -----------
# st.markdown('<div class="form-wrapper">', unsafe_allow_html=True)

# with st.container():
#     st.markdown('<div class="form-card">', unsafe_allow_html=True)
#     st.header("📄 Submit Your AIR Report")

#     with st.form("upload_form", clear_on_submit=True):
#         inspection_date = st.date_input("Inspection Date")
#         customer_name = st.text_input("Customer Name")
#         screen = st.text_input("Screen", placeholder="Dry, Wet, etc.")
#         screen_type = st.text_input("Screen Type")
#         aperture_dim = st.number_input("Aperture Dimension (mm)", min_value=0.0, format="%.2f")
#         aperture_shape = st.text_input("Aperture Shape")
#         panel_rows = st.number_input("Panel - Rows", min_value=1, step=1, format="%d")
#         panel_cols = st.number_input("Panel - Columns", min_value=1, step=1, format="%d")
#         receiver_email = st.text_input("Recipient Email")
#         uploaded_file = st.file_uploader("Upload ZIP file", type=["zip"])
#         submit = st.form_submit_button("Generate Report")
#     st.markdown('</div>', unsafe_allow_html=True)

# st.markdown('</div>', unsafe_allow_html=True)

# # ----------- Helper: Get Access Token -----------
# def get_dropbox_access_token():
#     response = requests.post("https://api.dropboxapi.com/oauth2/token", data={
#         "grant_type": "refresh_token",
#         "refresh_token": DROPBOX_REFRESH_TOKEN,
#         "client_id": DROPBOX_APP_KEY,
#         "client_secret": DROPBOX_APP_SECRET
#     })
#     return response.json().get("access_token")

# # ----------- Dropbox Upload Function -----------
# def upload_to_dropbox(file, filename):
#     try:
#         access_token = get_dropbox_access_token()
#         dbx = dropbox.Dropbox(access_token)
#         dropbox_path = f"/AIR_Uploads/{filename}"
#         dbx.files_upload(file.getvalue(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
#         shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
#         return shared_link_metadata.url.replace("?dl=0", "?dl=1")
#     except Exception as e:
#         st.error(f"❌ Dropbox upload error: {str(e)}")
#         return None

# # ----------- Submission Logic -----------
# if submit:
#     if not uploaded_file:
#         st.error("Please upload a ZIP file.")
#     elif uploaded_file.size > MAX_MB * 1024 * 1024:
#         st.error(f"⚠️ File size exceeds {MAX_MB}MB limit.")
#     elif not customer_name or not screen or not screen_type or not aperture_shape or not receiver_email:
#         st.error("Please complete all required fields.")
#     else:
#         with st.spinner("⏳ Uploading and processing your submission..."):
#             try:
#                 link = upload_to_dropbox(uploaded_file, uploaded_file.name)

#                 if not link:
#                     st.error("❌ Dropbox upload failed.")
#                 else:
#                     # --- Email to Self ---
#                     email_self = EmailMessage()
#                     email_self["Subject"] = f"New AIR Submission from {customer_name}"
#                     email_self["From"] = SENDER_EMAIL
#                     email_self["To"] = RECEIVER_EMAIL_SELF
#                     body = f"""
# New AIR Submission Received:

# Inspection Date: {inspection_date}
# Customer: {customer_name}
# Screen: {screen}
# Screen Type: {screen_type}
# Aperture Dimension: {aperture_dim} mm
# Aperture Shape: {aperture_shape}
# Panels: {panel_rows} Rows x {panel_cols} Columns

# Download File: {link}
#                     """
#                     email_self.set_content(body)

#                     # --- Email to Recipient ---
#                     email_client = EmailMessage()
#                     email_client["Subject"] = "AIR Submission Received"
#                     email_client["From"] = SENDER_EMAIL
#                     email_client["To"] = receiver_email
#                     email_client.set_content(
#                         "Dear User,\n\nYour data has been received successfully and is currently in queue for processing.\n"
#                         "It typically takes up to **2 hours** to generate the final report.\n\n"
#                         "Best regards,\nFLS Automation Team"
#                     )

#                     # --- Send Emails ---
#                     context = ssl.create_default_context()
#                     with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
#                         server.login(SENDER_EMAIL, SENDER_PASSWORD)
#                         server.send_message(email_self)
#                         server.send_message(email_client)

#                     # --- Success Card ---
#                     st.markdown("""
#                         <div class="note">
#                             ✅ <strong>Submission successful!</strong><br>
#                             Your file has been received. You’ll receive your report by email within 2 hours.
#                         </div>
#                     """, unsafe_allow_html=True)

#             except Exception as e:
#                 st.error(f"❌ Failed to send emails: {str(e)}")
                

# st.markdown("""
#     <style>
#     #MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}
#     header {visibility: hidden;}
#     .stDeployButton {display: none;}
#     .viewerBadge_container__1QSob {display: none !important;}
#     </style>
# """, unsafe_allow_html=True)

import streamlit as st
import smtplib
import ssl
from email.message import EmailMessage
import dropbox
from dotenv import load_dotenv
import os
import requests

# ----------- LOAD SECRETS -----------
load_dotenv()

DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL_SELF = os.getenv("RECEIVER_EMAIL_SELF")
MAX_MB = 100

# ----------- PAGE SETUP & STYLING -----------
st.set_page_config(page_title="AIR Report Upload", layout="centered")

st.markdown("""
    <style>
    body, .main {
        background-color: #062f5f;
        color: white;
    }
    .form-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    .form-card {
        color: black !important;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        max-width: 700px;
        width: 100%;
    }
    .thin-line {
        height: 1px;
        background-color: white;
        border: none;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .note {
        background-color: white;
        color: black;
        padding: 1rem;
        border-left: 6px solid #4CAF50;
        border-radius: 8px;
        margin-top: 1.5rem;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #062f5f;
        color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 0.85rem;
        z-index: 999;
    }
    header, .block-container {
        padding-top: 2rem !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .viewerBadge_container__1QSob {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# ----------- HEADER SECTION -----------
st.image("assets/logo.png", width=120)
st.markdown('<hr class="thin-line">', unsafe_allow_html=True)

# ----------- FORM CENTERED -----------
st.markdown('<div class="form-wrapper">', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.header("📄 Generate Your AIR Report")

    with st.form("upload_form", clear_on_submit=True):
        inspection_date = st.date_input("Inspection Date")
        customer_name = st.text_input("Customer Name")
        screen = st.text_input("Screen", placeholder="Dry, Wet, etc.")
        screen_type = st.text_input("Screen Type")
        aperture_dim = st.number_input("Aperture Dimension (mm)", min_value=0.0, format="%.2f")
        aperture_shape = st.text_input("Aperture Shape")
        panel_rows = st.number_input("Panel - Rows", min_value=1, step=1, format="%d")
        panel_cols = st.number_input("Panel - Columns", min_value=1, step=1, format="%d")
        receiver_email = st.text_input("Recipient Email")
        uploaded_file = st.file_uploader("Upload ZIP file", type=["zip"])
        submit = st.form_submit_button("Generate Report")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ----------- FOOTER -----------
st.markdown('<div class="footer">© 2025 FLS Automation | All rights reserved</div>', unsafe_allow_html=True)

# ----------- Helper: Get Access Token -----------
def get_dropbox_access_token():
    response = requests.post("https://api.dropboxapi.com/oauth2/token", data={
        "grant_type": "refresh_token",
        "refresh_token": DROPBOX_REFRESH_TOKEN,
        "client_id": DROPBOX_APP_KEY,
        "client_secret": DROPBOX_APP_SECRET
    })
    return response.json().get("access_token")

# ----------- Dropbox Upload Function -----------
def upload_to_dropbox(file, filename):
    try:
        access_token = get_dropbox_access_token()
        dbx = dropbox.Dropbox(access_token)
        dropbox_path = f"/AIR_Uploads/{filename}"
        dbx.files_upload(file.getvalue(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
        try:
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
        except dropbox.exceptions.ApiError as e:
            if isinstance(e.error, dropbox.sharing.CreateSharedLinkWithSettingsError) and e.error.is_shared_link_already_exists():
                shared_links = dbx.sharing_list_shared_links(path=dropbox_path, direct_only=True).links
                if shared_links:
                    shared_link_metadata = shared_links[0]
                else:
                    raise e
            else:
                raise e
        return shared_link_metadata.url.replace("?dl=0", "?dl=1")
    except Exception as e:
        st.error(f"❌ Dropbox upload error: {str(e)}")
        return None

# ----------- Submission Logic -----------
if submit:
    if not uploaded_file:
        st.error("Please upload a ZIP file.")
    elif uploaded_file.size > MAX_MB * 1024 * 1024:
        st.error(f"⚠️ File size exceeds {MAX_MB}MB limit.")
    elif not customer_name or not screen or not screen_type or not aperture_shape or not receiver_email:
        st.error("Please complete all required fields.")
    else:
        with st.spinner("⏳ Uploading and processing your submission..."):
            try:
                link = upload_to_dropbox(uploaded_file, uploaded_file.name)

                if not link:
                    st.error("❌ Dropbox upload failed.")
                else:
                    email_self = EmailMessage()
                    email_self["Subject"] = f"New AIR Submission from {customer_name}"
                    email_self["From"] = SENDER_EMAIL
                    email_self["To"] = RECEIVER_EMAIL_SELF
                    body = f"""
New AIR Submission Received:

Inspection Date: {inspection_date}
Customer: {customer_name}
Screen: {screen}
Screen Type: {screen_type}
Aperture Dimension: {aperture_dim} mm
Aperture Shape: {aperture_shape}
Panels: {panel_rows} Rows x {panel_cols} Columns

Download File: {link}
                    """
                    email_self.set_content(body)

                    email_client = EmailMessage()
                    email_client["Subject"] = "AIR Submission Received"
                    email_client["From"] = SENDER_EMAIL
                    email_client["To"] = receiver_email
                    email_client.set_content(
                        "Dear User,\n\nYour data has been received successfully and is currently in queue for processing.\n"
                        "It typically takes up to 2 hours to generate the final report.\n\n"
                        "Best regards,\nAIRA Automation Team"
                    )

                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                        server.login(SENDER_EMAIL, SENDER_PASSWORD)
                        server.send_message(email_self)
                        server.send_message(email_client)

                    st.markdown("""
                        <div class="note">
                            ✅ <strong>Submission successful!</strong><br>
                            Your file has been received. You’ll receive your report by email within 2 hours.
                        </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Failed to send emails: {str(e)}")


