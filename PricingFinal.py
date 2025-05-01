import streamlit as st
import math
import pandas as pd
import fitz
from PIL import Image
import smtplib
import os
from email.message import EmailMessage
from datetime import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="BeyondSkool Pricing Wizard", layout="centered")

# ---------- BRANDING ----------
logo = Image.open("BeyondSkool_logo.png")
st.image(logo, use_container_width=True)
st.title("BeyondSkool Pricing Wizard")
st.markdown("Empowering Schools with Transformative Learning Programs")

# ---------- INPUT SECTION ----------
school_name = st.text_input("🏫 Name of the School")
your_email = st.text_input("📧 Your Email ID (BeyondSkool Creator)")
school_email = st.text_input("🏫 School's Email ID")
programs_selected = st.multiselect("📚 Select Program(s):", ["Communication", "Financial Literacy", "STEM"])
school_days = st.radio("📅 School operates:", ["5 days a week", "6 days a week"], horizontal=True)
max_sections_per_teacher = 27 if school_days == "5 days a week" else 32

student_info = {}
if programs_selected:
    for prog in programs_selected:
        students = st.number_input(f"🎓 Number of Students - {prog}", min_value=50, max_value=3000, step=50, key=f"students_{prog}")
        section_size = st.number_input(f"👩‍🏫 Students per Section - {prog}", min_value=10, max_value=60, step=5, value=30, key=f"section_{prog}")
        student_info[prog] = {"students": students, "section_size": section_size}

    if st.button("Calculate Pricing"):
        st.session_state.update({
            "school_name": school_name,
            "your_email": your_email,
            "school_email": school_email,
            "programs_selected": programs_selected,
            "student_info": student_info,
            "school_days": school_days,
            "calculate": True,
            "confirm": False
        })

# ---------- PRICING OUTPUT ----------
if st.session_state.get("calculate"):
    discount_percent = st.slider("🎯 Discount %", 0, 40, 0)

    student_info = st.session_state["student_info"]
    programs_selected = st.session_state["programs_selected"]
    school_name = st.session_state["school_name"]
    school_days = st.session_state["school_days"]
    max_sections_per_teacher = 27 if school_days == "5 days a week" else 32

    total_cost = 0
    total_students = 0
    total_final_price = 0
    program_blocks = []

    for prog in programs_selected:
        data = student_info[prog]
        students = data["students"]
        section_size = data["section_size"]
        sections = math.ceil(students / section_size)

        full_teachers = 0
        variable_teacher_days = 0
        teacher_day_cost = 0

        if sections < 20:
            full_teachers = 0
            variable_teacher_days = math.ceil(sections / 5)
            teacher_day_cost = variable_teacher_days * 2000 * 35
        else:
            full_teachers = sections // max_sections_per_teacher
            remaining = sections % max_sections_per_teacher
            if 0 < remaining < 20:
                variable_teacher_days = math.ceil(remaining / 5)
                teacher_day_cost = variable_teacher_days * 2000 * 35
            elif remaining >= 20:
                full_teachers += 1
                variable_teacher_days = 0
                teacher_day_cost = 0

            # Add 10% coverage for full-time teachers' absence via variable teachers
            full_time_sessions = full_teachers * max_sections_per_teacher * 35
            absent_sessions = math.ceil(full_time_sessions * 0.10)
            absent_days = math.ceil(absent_sessions / 5)
            teacher_day_cost += absent_days * 2000

        teacher_cost = 425000 if prog == "STEM" else 400000
        teacher_cost_total = full_teachers * teacher_cost
        book_cost = students * 200
        kit_cost = 115000 if prog == "STEM" else 0
        manager_cost = 50000

        program_cost = teacher_cost_total + teacher_day_cost + book_cost + kit_cost
        total_program_cost = program_cost + manager_cost

        base_price = total_program_cost / (1 - 0.4)
        final_price = base_price * (1 - discount_percent / 100)
        price_per_student = final_price / students

        total_cost += total_program_cost
        total_students += students
        total_final_price += final_price

        program_blocks.append({
            "Program": prog,
            "Students": students,
            "Sections": sections,
            "Full-Time Teachers": full_teachers,
            "Variable Teacher Days": variable_teacher_days,
            "Price per Student": round(price_per_student),
            "Total Program Price": round(final_price)
        })

    gross_margin = ((total_final_price - total_cost) / total_final_price) * 100
    st.markdown(f"""<div style='position:fixed; bottom:10px; right:10px; color:white; background-color:white; padding:5px; border-radius:5px; font-size:10px;'>Gross Margin: {gross_margin:.2f}%</div>""", unsafe_allow_html=True)

    if gross_margin < 30:
        st.error(" No Pricing can be offered.")
    else:
        st.header("📊 Pricing Summary")
        for block in program_blocks:
            st.markdown(f"""
            ### 📚 {block['Program']}
            - 🎓 Students: {block['Students']}
            - 📈 Sections: {block['Sections']}
            - 👩‍🏫 Full-Time Teachers: {block['Full-Time Teachers']}
            - 👨‍🏫 Variable Teacher Days: {block['Variable Teacher Days']}
            - 💰 Price per Student: Rs.{block['Price per Student']}
            - 💵 Total Program Price: Rs.{block['Total Program Price']:,}
            """)

        st.subheader(f"Total Price: Rs.{round(total_final_price):,}")
        st.subheader(f"Average Price per Student: Rs.{round(total_final_price / total_students)}")

        if not st.session_state.get("confirm"):
            if st.button("✅ Confirm Pricing"):
                st.session_state["confirm"] = True

# (SPA generation, commercial table, and email logic would continue here…)
