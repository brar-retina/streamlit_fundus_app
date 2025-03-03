# app.py
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import io
import json
from data_manager import DataManager
import base64

# Initialize session state
if 'app_state' not in st.session_state:
    st.session_state.app_state = {
        'current_patient': None,
        'left_drawings': [],
        'right_drawings': [],
        'legend_data': [],
        'left_history': [],
        'right_history': [],
        'drawing_mode': 'line',
        'editing_mode': 'draw',
        'drawing_color': 'red',
        'fill_type': 'none',
        'opacity': 0.7,
        'line_width': 2,
        'current_eye': None,
        'patient_name': '',
        'patient_age': '',
        'diagnosis': '',
        'diagnosis_other': '',
        'left_eye': '',
        'right_eye': '',
        'va_left': '',
        'va_right': '',
        'iop_left': '',
        'iop_right': ''
    }

def main():
    st.set_page_config(page_title="Retinal Fundus Chart Generator", layout="wide")
    st.title("Retinal Fundus Chart Generator")

    # Initialize DataManager
    data_manager = DataManager("patient_data")

    # Sidebar for patient info
    with st.sidebar:
        st.header("Patient Information")
        
        patient_id = st.text_input("Patient ID", value=st.session_state.app_state['current_patient'] or "")
        st.session_state.app_state['current_patient'] = patient_id
        
        patient_name = st.text_input("Patient Name", value=st.session_state.app_state['patient_name'])
        st.session_state.app_state['patient_name'] = patient_name
        
        patient_age = st.text_input("Age", value=st.session_state.app_state['patient_age'])
        st.session_state.app_state['patient_age'] = patient_age
        
        diagnosis = st.selectbox("Diagnosis", [
            "Diabetic Retinopathy",
            "Age-related Macular Degeneration",
            "Retinal Detachment",
            "Glaucoma",
            "Retinitis Pigmentosa",
            "Other"
        ], index=["Diabetic Retinopathy", "Age-related Macular Degeneration", "Retinal Detachment", 
                  "Glaucoma", "Retinitis Pigmentosa", "Other"].index(st.session_state.app_state['diagnosis']) if st.session_state.app_state['diagnosis'] else 0)
        st.session_state.app_state['diagnosis'] = diagnosis
        
        diagnosis_other = st.text_input("Specify Other Diagnosis", value=st.session_state.app_state['diagnosis_other']) if diagnosis == "Other" else ""
        st.session_state.app_state['diagnosis_other'] = diagnosis_other
        
        st.subheader("Retinal Findings")
        right_eye = st.text_input("Right Eye", value=st.session_state.app_state['right_eye'])
        st.session_state.app_state['right_eye'] = right_eye
        
        left_eye = st.text_input("Left Eye", value=st.session_state.app_state['left_eye'])
        st.session_state.app_state['left_eye'] = left_eye
        
        col1, col2 = st.columns(2)
        with col1:
            va_right = st.text_input("VA Right", value=st.session_state.app_state['va_right'])
            st.session_state.app_state['va_right'] = va_right
            iop_right = st.text_input("IOP Right (mmHg)", value=st.session_state.app_state['iop_right'])
            st.session_state.app_state['iop_right'] = iop_right
        with col2:
            va_left = st.text_input("VA Left", value=st.session_state.app_state['va_left'])
            st.session_state.app_state['va_left'] = va_left
            iop_left = st.text_input("IOP Left (mmHg)", value=st.session_state.app_state['iop_left'])
            st.session_state.app_state['iop_left'] = iop_left

        # Patient management buttons
        if st.button("Load Patient"):
            if patient_id:
                patient_data = data_manager.load_patient(patient_id)
                if patient_data:
                    st.session_state.app_state.update({
                        'current_patient': patient_id,
                        'patient_name': patient_data.get("name", ""),
                        'patient_age': patient_data.get("age", ""),
                        'diagnosis': patient_data.get("diagnosis", ""),
                        'diagnosis_other': patient_data.get("diagnosis_other", ""),
                        'left_eye': patient_data.get("left_eye", ""),
                        'right_eye': patient_data.get("right_eye", ""),
                        'va_left': patient_data.get("va_left", ""),
                        'va_right': patient_data.get("va_right", ""),
                        'iop_left': patient_data.get("iop_left", ""),
                        'iop_right': patient_data.get("iop_right", ""),
                        'left_drawings': patient_data.get("left_drawings", []),
                        'right_drawings': patient_data.get("right_drawings", []),
                        'legend_data': patient_data.get("legend_data", [])
                    })
                    st.success(f"Loaded patient {patient_id}")
                else:
                    st.error("Patient not found")
            else:
                st.error("Please enter a Patient ID")
        
        if st.button("Save Patient"):
            if patient_id:
                patient_data = {
                    "id": patient_id,
                    "name": st.session_state.app_state['patient_name'],
                    "age": st.session_state.app_state['patient_age'],
                    "diagnosis": st.session_state.app_state['diagnosis'],
                    "diagnosis_other": st.session_state.app_state['diagnosis_other'],
                    "left_eye": st.session_state.app_state['left_eye'],
                    "right_eye": st.session_state.app_state['right_eye'],
                    "va_right": st.session_state.app_state['va_right'],
                    "va_left": st.session_state.app_state['va_left'],
                    "iop_right": st.session_state.app_state['iop_right'],
                    "iop_left": st.session_state.app_state['iop_left'],
                    "left_drawings": st.session_state.app_state['left_drawings'],
                    "right_drawings": st.session_state.app_state['right_drawings'],
                    "legend_data": st.session_state.app_state['legend_data'],
                    "provider": "Streamlit User"
                }
                data_manager.save_complete_patient_record(patient_id, patient_data)
                st.session_state.app_state['current_patient'] = patient_id
                st.success(f"Saved patient {patient_id}")
            else:
                st.error("Please enter a Patient ID")

        if st.button("New Patient"):
            st.session_state.app_state.update({
                'current_patient': None,
                'patient_name': '',
                'patient_age': '',
                'diagnosis': '',
                'diagnosis_other': '',
                'left_eye': '',
                'right_eye': '',
                'va_left': '',
                'va_right': '',
                'iop_left': '',
                'iop_right': '',
                'left_drawings': [],
                'right_drawings': [],
                'legend_data': [],
                'left_history': [],
                'right_history': []
            })
            st.experimental_rerun()

    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Drawing Tools")
        edit_mode = st.radio("Mode", ["Draw", "Transform", "Delete"], horizontal=True)
        st.session_state.app_state['editing_mode'] = edit_mode.lower()
        
        drawing_tool = st.selectbox("Tool", ["Line", "Rectangle", "Circle", "Dot", "Freehand", "Polygon"], format_func=lambda x: x, label_visibility="collapsed")
        st.session_state.app_state['drawing_mode'] = drawing_tool.lower()
        
        color = st.selectbox("Color", ["red", "green", "blue", "yellow", "black", "purple", "orange", "brown"], format_func=lambda x: x, label_visibility="collapsed")
        st.session_state.app_state['drawing_color'] = color
        
        fill_type = st.selectbox("Fill", ["none", "solid"], format_func=lambda x: x, label_visibility="collapsed")
        st.session_state.app_state['fill_type'] = fill_type
        
        opacity = st.slider("Opacity", 0.1, 1.0, 0.7, format="%.1f", label_visibility="collapsed")
        st.session_state.app_state['opacity'] = opacity
        
        line_width = st.slider("Width", 1, 10, 2, label_visibility="collapsed")
        st.session_state.app_state['line_width'] = line_width

        # Generate base chart
        fig = generate_base_chart(
            st.session_state.app_state['patient_name'],
            st.session_state.app_state['current_patient'],
            st.session_state.app_state['patient_age'],
            st.session_state.app_state['diagnosis'],
            st.session_state.app_state['diagnosis_other'],
            st.session_state.app_state['left_eye'],
            st.session_state.app_state['right_eye'],
            st.session_state.app_state['va_left'],
            st.session_state.app_state['va_right'],
            st.session_state.app_state['iop_left'],
            st.session_state.app_state['iop_right']
        )
        
        # Convert Matplotlib figure to image for canvas background
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=100, bbox_inches='tight')
        buf.seek(0)
        img = Image.open(buf)
        
        # Display canvases side by side
        col_right, col_left = st.columns(2)
        
        # Prepare drawing settings
        stroke_color = st.session_state.app_state['drawing_color']
        stroke_width = st.session_state.app_state['line_width']
        drawing_mode = st.session_state.app_state['drawing_mode']
        if drawing_mode == "freehand":
            drawing_mode = "freedraw"
        elif drawing_mode == "polygon":
            drawing_mode = "polygon"
        elif drawing_mode == "line":
            drawing_mode = "line"
        elif drawing_mode == "rectangle":
            drawing_mode = "rect"
        elif drawing_mode == "circle":
            drawing_mode = "circle"
        elif drawing_mode == "dot":
            drawing_mode = "point"

        canvas_width = 400  # Reduced width for side-by-side display
        canvas_height = 400
        
        with col_right:
            st.write("Right Eye (O.D.)")
            right_canvas_result = st_canvas(
                fill_color=f"rgba({','.join(map(str, Image.new('RGB', (1,1), stroke_color).getpixel((0,0))))},{opacity})" if fill_type == "solid" else "rgba(0,0,0,0)",
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_image=img,
                update_streamlit=True,
                height=canvas_height,
                width=canvas_width,
                drawing_mode=drawing_mode if edit_mode == "Draw" else "transform",
                key="right_canvas",
                display_toolbar=True,
            )

        with col_left:
            st.write("Left Eye (O.S.)")
            left_canvas_result = st_canvas(
                fill_color=f"rgba({','.join(map(str, Image.new('RGB', (1,1), stroke_color).getpixel((0,0))))},{opacity})" if fill_type == "solid" else "rgba(0,0,0,0)",
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_image=img,
                update_streamlit=True,
                height=canvas_height,
                width=canvas_width,
                drawing_mode=drawing_mode if edit_mode == "Draw" else "transform",
                key="left_canvas",
                display_toolbar=True,
            )

        # Process canvas drawings
        if right_canvas_result.json_data:
            process_canvas_data(right_canvas_result.json_data, "right")
        if left_canvas_result.json_data:
            process_canvas_data(left_canvas_result.json_data, "left")

        # Chart controls
        if st.button("Save Chart"):
            save_chart(data_manager, patient_id)

    with col2:
        st.subheader("Legend")
        legend_label = st.text_input("Legend Label")
        if st.button("Add to Legend"):
            if legend_label:
                st.session_state.app_state['legend_data'].append({
                    "label": legend_label,
                    "color": st.session_state.app_state['drawing_color'],
                    "fill_type": st.session_state.app_state['fill_type'],
                    "alpha": st.session_state.app_state['opacity'],
                    "line_width": st.session_state.app_state['line_width']
                })
        
        for i, item in enumerate(st.session_state.app_state['legend_data']):
            st.write(f"{item['label']} - {item['color']}")

def generate_base_chart(name, pid, age, diagnosis, diagnosis_other, left_eye, right_eye, 
                       va_left, va_right, iop_left, iop_right):
    fig = plt.figure(figsize=(10, 5))
    gs = fig.add_gridspec(1, 3)
    
    right_ax = fig.add_subplot(gs[0, 0], aspect='equal')
    left_ax = fig.add_subplot(gs[0, 1], aspect='equal')
    legend_ax = fig.add_subplot(gs[0, 2])
    legend_ax.axis('off')
    
    draw_eye_chart(right_ax, "Right Eye", right_eye, va_right, iop_right)
    draw_eye_chart(left_ax, "Left Eye", left_eye, va_left, iop_left)
    
    diag_text = diagnosis if diagnosis != "Other" else f"Other: {diagnosis_other}"
    fig.suptitle(f"Patient: {name} | ID: {pid} | Age: {age} | Diagnosis: {diag_text}", fontsize=9)
    
    draw_legend(legend_ax)
    
    fig.tight_layout()
    return fig

def draw_eye_chart(ax, title, findings, va, iop):
    ax.clear()
    for r in [1.0, 0.8, 0.6]:
        ax.add_patch(plt.Circle((0, 0), r, fill=False, color='black'))
    
    for hour in range(1, 13):
        angle = np.radians(90 - hour * 30)
        x_label, y_label = 1.1 * np.cos(angle), 1.1 * np.sin(angle)
        ax.text(x_label, y_label, str(hour), ha='center', va='center', fontsize=8)
        x1, y1 = 0.4 * np.cos(angle), 0.4 * np.sin(angle)
        x2, y2 = 1.0 * np.cos(angle), 1.0 * np.sin(angle)
        ax.plot([x1, x2], [y1, y2], 'k-', linewidth=0.5)
    
    eye_abbr = "O.D." if title == "Right Eye" else "O.S."
    ax.set_title(f"{eye_abbr}\nVA: {va} | IOP: {iop} mmHg")
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.axis('off')

def process_canvas_data(canvas_data, eye):
    drawings = st.session_state.app_state[f'{eye}_drawings']
    objects = canvas_data.get("objects", [])
    
    # Clear existing drawings for this eye
    drawings.clear()
    
    for obj in objects:
        if obj["type"] in ["path", "rect", "line", "circle", "point"]:
            color = f"#{obj['stroke'][1:]}" if obj['stroke'].startswith('#') else obj['stroke']
            drawing_data = {
                "type": obj["type"],
                "color": color,
                "width": obj["strokeWidth"],
                "alpha": obj.get("opacity", st.session_state.app_state['opacity'])
            }
            
            if obj["type"] == "path":
                drawing_data["points"] = obj["path"]
                drawing_data["type"] = "freehand"
            elif obj["type"] == "rect":
                drawing_data["coords"] = ((obj["left"], obj["top"]), obj["width"], obj["height"])
                drawing_data["fill"] = "solid" if obj["fill"] != "transparent" else "none"
            elif obj["type"] == "line":
                drawing_data["coords"] = ((obj["x1"], obj["y1"]), (obj["x2"], obj["y2"]))
            elif obj["type"] == "circle":
                drawing_data["coords"] = ((obj["left"] + obj["radius"], obj["top"] + obj["radius"]), obj["radius"])
                drawing_data["fill"] = "solid" if obj["fill"] != "transparent" else "none"
            elif obj["type"] == "point":
                drawing_data["coords"] = (obj["left"], obj["top"])
                drawing_data["radius"] = 5  # Fixed size for dot
            
            drawings.append(drawing_data)

def draw_legend(ax):
    y_pos = 0.9
    for item in st.session_state.app_state['legend_data']:
        if item["fill_type"] == "none":
            ax.plot([0.1, 0.3], [y_pos, y_pos], color=item["color"], linewidth=item["line_width"])
        else:
            rect = plt.Rectangle((0.1, y_pos-0.03), 0.2, 0.06, color=item["color"], 
                               alpha=item["alpha"], linewidth=item["line_width"])
            ax.add_patch(rect)
        ax.text(0.35, y_pos, item["label"], va='center', fontsize=9)
        y_pos -= 0.1

def save_chart(data_manager, patient_id):
    if not patient_id:
        st.error("Please enter a patient ID first")
        return
    
    fig = generate_base_chart(
        st.session_state.app_state['patient_name'],
        patient_id,
        st.session_state.app_state['patient_age'],
        st.session_state.app_state['diagnosis'],
        st.session_state.app_state['diagnosis_other'],
        st.session_state.app_state['left_eye'],
        st.session_state.app_state['right_eye'],
        st.session_state.app_state['va_left'],
        st.session_state.app_state['va_right'],
        st.session_state.app_state['iop_left'],
        st.session_state.app_state['iop_right']
    )
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    buf.seek(0)
    image_bytes = buf.getvalue()
    filename = data_manager.save_chart_image(patient_id, image_bytes)
    st.success(f"Chart saved as {filename}")

if __name__ == "__main__":
    main()
