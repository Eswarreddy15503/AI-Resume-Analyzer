import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Blue palette colors
BLUE_DARK = "#1E3A8A"   # Navy
BLUE_PRIMARY = "#3B82F6" # Vibrant Blue
BLUE_LIGHT = "#93C5FD"  # Soft Blue
BLUE_BG = "#F0FDF4"     # Light background accent (not blue, but we'll use light blue #EFF6FF)
BLUE_MUTED = "#EFF6FF"

def create_ats_gauge(score: int):
    """
    Creates an ATS Score Gauge using Plotly.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall ATS Compatibility", 'font': {'size': 20, 'color': BLUE_DARK, 'family': 'sans-serif'}},
        number={'font': {'color': BLUE_DARK, 'family': 'sans-serif', 'size': 50}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': BLUE_DARK},
            'bar': {'color': BLUE_PRIMARY},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E5E7EB",
            'steps': [
                {'range': [0, 50], 'color': '#EFF6FF'},
                {'range': [50, 75], 'color': '#DBEAFE'},
                {'range': [75, 100], 'color': '#BFDBFE'}
            ],
            'threshold': {
                'line': {'color': BLUE_DARK, 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        height=280
    )
    
    return fig

def create_skills_chart(skills_dict: dict):
    """
    Creates a bar chart showing the count of skills in each category.
    """
    categories = list(skills_dict.keys())
    counts = [len(lst) for lst in skills_dict.values()]
    
    df = pd.DataFrame({
        "Category": categories,
        "Skills Count": counts
    })
    
    # Sort by count
    df = df.sort_values(by="Skills Count", ascending=True)
    
    fig = go.Figure(go.Bar(
        x=df["Skills Count"],
        y=df["Category"],
        orientation='h',
        marker=dict(
            color=df["Skills Count"],
            colorscale=[[0, BLUE_LIGHT], [1, BLUE_PRIMARY]],
            line=dict(color=BLUE_DARK, width=1)
        ),
        text=df["Skills Count"],
        textposition='auto',
    ))
    
    fig.update_layout(
        title={'text': "Skills Distribution by Category", 'font': {'color': BLUE_DARK, 'size': 16}},
        xaxis=dict(title="Number of Skills", gridcolor="#E5E7EB"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        height=280
    )
    
    return fig

def create_completeness_chart(sections_dict: dict):
    """
    Creates a horizontal completion bar chart of sections.
    """
    sections_labels = {
        "education": "Education",
        "experience": "Work Experience",
        "skills_raw": "Skills List",
        "projects": "Projects",
        "certifications": "Certifications"
    }
    
    labels = []
    completion = []
    
    for sec, display_name in sections_labels.items():
        labels.append(display_name)
        val = len(sections_dict.get(sec, "").strip())
        # Completion indicator: check character length
        if val > 150:
            completion.append(100)
        elif val > 50:
            completion.append(70)
        elif val > 10:
            completion.append(40)
        else:
            completion.append(10)
            
    df = pd.DataFrame({
        "Section": labels,
        "Completeness %": completion
    })
    
    # Sort
    df = df.sort_values(by="Completeness %", ascending=True)
    
    fig = go.Figure(go.Bar(
        x=df["Completeness %"],
        y=df["Section"],
        orientation='h',
        marker=dict(
            color=BLUE_PRIMARY,
            line=dict(color=BLUE_DARK, width=1)
        ),
        text=df["Completeness %"].apply(lambda val: f"{val}%"),
        textposition='inside',
        textfont=dict(color="white")
    ))
    
    fig.update_layout(
        title={'text': "Resume Section Completeness", 'font': {'color': BLUE_DARK, 'size': 16}},
        xaxis=dict(title="Completion %", range=[0, 105], gridcolor="#E5E7EB"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        height=280
    )
    
    return fig

def create_jd_match_gauge(match_percentage: int):
    """
    Creates a simple, neat match percentage radial gauge.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=match_percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Job Description Match", 'font': {'size': 18, 'color': BLUE_DARK, 'family': 'sans-serif'}},
        number={'font': {'color': BLUE_DARK, 'size': 40}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': BLUE_PRIMARY},
            'bar': {'color': BLUE_PRIMARY},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E5E7EB",
            'steps': [
                {'range': [0, 45], 'color': '#EFF6FF'},
                {'range': [45, 70], 'color': '#DBEAFE'},
                {'range': [70, 100], 'color': '#BFDBFE'}
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=10),
        height=220
    )
    
    return fig

def create_keyword_comparison_chart(comparison_list: list):
    """
    Creates a grouped horizontal bar chart comparing keyword frequency in JD vs Resume.
    """
    if not comparison_list:
        # Return empty figure
        return go.Figure()
        
    df = pd.DataFrame(comparison_list)
    # Sort by JD count
    df = df.sort_values(by="jd_count", ascending=True)
    
    fig = go.Figure()
    
    # Job Description frequencies
    fig.add_trace(go.Bar(
        y=df["keyword"],
        x=df["jd_count"],
        name='Job Description',
        orientation='h',
        marker=dict(color=BLUE_PRIMARY, line=dict(color=BLUE_DARK, width=1))
    ))
    
    # Resume frequencies
    fig.add_trace(go.Bar(
        y=df["keyword"],
        x=df["resume_count"],
        name='Your Resume',
        orientation='h',
        marker=dict(color=BLUE_LIGHT, line=dict(color=BLUE_DARK, width=1))
    ))
    
    fig.update_layout(
        title={'text': "Top Keyword Density (JD vs. Resume)", 'font': {'color': BLUE_DARK, 'size': 16}},
        barmode='group',
        xaxis=dict(title="Word Frequency / Occurrence Count", gridcolor="#E5E7EB"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        height=380
    )
    
    return fig
