import streamlit as st
import pandas as pd
from Match_tabs.Basic_tabs.basic_tab import BaseTab

# passing
class PassTab(BaseTab):
    def __init__(self):
        super().__init__("passing")
    
    def add_custom_plot(self):
        pass



# # def load_pass_tab():
#     st.header("⚽ Match Statistics")

#     data = load_data()

#     stats = {
#         "Shots": [7, 20, "🎯","./img_22.jpg"],
#         "Shots on Target": [2, 8, "🥅",""],
#         "Possession %": [36, 64, "⚽",""],
#         "Passes": [366, 623, "🔄",""],
#         "Pass Accuracy %": [81, 89, "📊",""],
#         "Fouls": [13, 12, "🟨",""],
#         "Yellow Cards": [2, 3, "🟡","./img_22.jpg"],
#         "Red Cards": [0, 1, "🔴","./img_22.jpg"],
#         "Offsides": [1, 3, "🚩","./img_22.jpg"],
#         "Corners": [2, 3, "📐","./img_22.jpg"]
#     }

#     # Add custom CSS for enhanced styling
#     # st.markdown("""
#     # <style>
#     # .stat-container {
#     #     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#     #     border-radius: 15px;
#     #     padding: 20px;
#     #     margin: 10px 0;
#     #     box-shadow: 0 4px 15px rgba(0,0,0,0.1);
#     # }
    
#     # .team-header {
#     #     text-align: center;
#     #     font-size: 1.5em;
#     #     font-weight: bold;
#     #     color: white;
#     #     margin-bottom: 20px;
#     #     padding: 10px;
#     #     border-radius: 10px;
#     # }
    
#     # .home-header {
#     #     background: linear-gradient(135deg, #2E86C1, #3498DB);
#     # }
    
#     # .away-header {
#     #     background: linear-gradient(135deg, #C0392B, #E74C3C);
#     # }
    
#     # .stat-row {
#     #     display: flex;
#     #     align-items: center;
#     #     justify-content: space-between;
#     #     background: rgba(255,255,255,0.95);
#     #     margin: 8px 0;
#     #     padding: 15px;
#     #     border-radius: 10px;
#     #     box-shadow: 0 2px 8px rgba(0,0,0,0.1);
#     #     transition: transform 0.2s ease;
#     # }
    
#     # .stat-row:hover {
#     #     transform: translateY(-2px);
#     #     box-shadow: 0 4px 12px rgba(0,0,0,0.15);
#     # }
    
#     # .stat-value {
#     #     font-size: 2em;
#     #     font-weight: bold;
#     #     text-align: center;
#     #     padding: 10px;
#     #     border-radius: 8px;
#     #     min-width: 80px;
#     # }
    
#     # .home-value {
#     #     color: #2E86C1;
#     #     background: linear-gradient(135deg, #EBF5FB, #D6EAF8);
#     # }
    
#     # .away-value {
#     #     color: #C0392B;
#     #     background: linear-gradient(135deg, #FADBD8, #F1948A);
#     # }
    
#     # .stat-name {
#     #     font-size: 1.1em;
#     #     font-weight: bold;
#     #     color: #2C3E50;
#     #     text-align: center;
#     #     flex-grow: 1;
#     #     display: flex;
#     #     align-items: center;
#     #     justify-content: center;
#     #     gap: 10px;
#     # }
    
#     # .stat-icon {
#     #     font-size: 1.3em;
#     # }
    
#     # .progress-bar {
#     #     height: 8px;
#     #     border-radius: 4px;
#     #     background: #ECF0F1;
#     #     margin: 5px 0;
#     #     overflow: hidden;
#     # }
    
#     # .progress-fill {
#     #     height: 100%;
#     #     transition: width 0.3s ease;
#     # }
    
#     # .home-progress {
#     #     background: linear-gradient(90deg, #2E86C1, #3498DB);
#     # }
    
#     # .away-progress {
#     #     background: linear-gradient(90deg, #C0392B, #E74C3C);
#     # }
    
#     # .comparison-container {
#     #     background: white;
#     #     border-radius: 15px;
#     #     padding: 20px;
#     #     margin: 20px 0;
#     #     box-shadow: 0 4px 20px rgba(0,0,0,0.1);
#     # }
#     # </style>
#     # """, unsafe_allow_html=True)

#     # Create enhanced table
#     st.markdown('<div class="comparison-container">', unsafe_allow_html=True)
    
#     # Team headers
#     col1, col2, col3 = st.columns([1, 1, 1])
    
#     with col1:
#         st.markdown(f'<div class="team-header home-header">🏠 {home_team}</div>', unsafe_allow_html=True)
    
#     with col2:
#         st.markdown('<div class="team-header" style="background: linear-gradient(135deg, #34495E, #2C3E50); color: white;">📊 Statistics</div>', unsafe_allow_html=True)
    
#     with col3:
#         st.markdown(f'<div class="team-header away-header">✈️ {away_team}</div>', unsafe_allow_html=True)

#     # Helper function: convert local image to base64
#     import base64
#     def get_base64_image(image_path):
#         with open(image_path, "rb") as f:
#             data = f.read()
#         return "data:image/png;base64," + base64.b64encode(data).decode()
    
#     # Render stats table with tooltips
#     for stat, values in stats.items():
#         home_val, away_val, icon, image_path = values

#         # If image provided, convert to base64
#         img_html = ""
#         if image_path:
#             img_url = get_base64_image(image_path)
#             img_html = f'<span class="tooltip-image"><img src="{img_url}"></span>'

#         # Calculate percentages
#         if "%" in stat:
#             home_pct, away_pct = home_val, away_val
#         else:
#             total = home_val + away_val
#             home_pct = (home_val / total * 100) if total > 0 else 0
#             away_pct = (away_val / total * 100) if total > 0 else 0

#         col1, col2, col3 = st.columns([1, 1, 1])

#         with col1:
#             st.markdown(f'''
#             <div class="stat-value home-value">
#                 {home_val}
#                 <div class="progress-bar">
#                     <div class="progress-fill home-progress" style="width: {home_pct}%;"></div>
#                 </div>
#             </div>
#             ''', unsafe_allow_html=True)

#         with col2:
#             st.markdown(f'''
#             <div class="stat-name tooltip">
#                 <span class="stat-icon">{icon}</span>
#                 <span>{stat}</span>
#                 {img_html}
#             </div>
#             ''', unsafe_allow_html=True)

#         with col3:
#             st.markdown(f'''
#             <div class="stat-value away-value">
#                 {away_val}
#                 <div class="progress-bar">
#                     <div class="progress-fill away-progress" style="width: {away_pct}%;"></div>
#                 </div>
#             </div>
#             ''', unsafe_allow_html=True)

#         st.markdown("<br>", unsafe_allow_html=True)

#     # Tooltip CSS
#     st.markdown("""
#     <style>
#     .tooltip {
#     position: relative;
#     display: inline-block;
#     }

#     .tooltip .tooltip-image {
#     visibility: hidden;
#     position: absolute;
#     z-index: 1;
#     top: 100%;
#     left: 50%;
#     transform: translateX(-50%);
#     background: white;
#     padding: 5px;
#     border: 1px solid #ccc;
#     border-radius: 8px;
#     box-shadow: 0px 4px 8px rgba(0,0,0,0.3);
#     }

#     .tooltip .tooltip-image img {
#     max-width: 500px;  /* adjust image size */
#     height: auto;
#     border-radius: 6px;
#     }

#     .tooltip:hover .tooltip-image {
#     visibility: visible;
#     }
#     </style>
#     """, unsafe_allow_html=True)

#     # Add summary insights
#     # st.markdown("---")
#     # col1, col2, col3 = st.columns(3)
    
#     # with col1:
#     #     st.metric(
#     #         label="🎯 Shot Efficiency", 
#     #         value=f"{(stats['Shots on Target'][0]/stats['Shots'][0]*100):.1f}%",
#     #         help=f"{home_team} shots on target percentage"
#     #     )
    
#     # with col2:
#     #     possession_diff = stats['Possession %'][1] - stats['Possession %'][0]
#     #     st.metric(
#     #         label="⚽ Possession Advantage", 
#     #         value=f"{away_team}",
#     #         delta=f"+{possession_diff}%"
#     #     )
    
#     # with col3:
#     #     st.metric(
#     #         label="🔴 Disciplinary", 
#     #         value=f"{stats['Yellow Cards'][0] + stats['Yellow Cards'][1]} Cards",
#     #         delta=f"{stats['Red Cards'][0] + stats['Red Cards'][1]} Red",
#     #         delta_color="inverse"
#     #     )

#     # # Additional insights section
#     # with st.expander("📈 Detailed Analysis", expanded=False):
#     #     col1, col2 = st.columns(2)
        
#     #     with col1:
#     #         st.subheader(f"🏠 {home_team} Highlights")
#     #         st.write(f"• Shot accuracy: {(stats['Shots on Target'][0]/stats['Shots'][0]*100):.1f}%")
#     #         st.write(f"• Pass accuracy: {stats['Pass Accuracy %'][0]}%")
#     #         st.write(f"• Fouls committed: {stats['Fouls'][0]}")
            
#     #     with col2:
#     #         st.subheader(f"✈️ {away_team} Highlights")
#     #         st.write(f"• Shot accuracy: {(stats['Shots on Target'][1]/stats['Shots'][1]*100):.1f}%")
#     #         st.write(f"• Pass accuracy: {stats['Pass Accuracy %'][1]}%")
#     #         st.write(f"• Fouls committed: {stats['Fouls'][1]}")

#     st.markdown("Pass network")
#     # display image in streamlit
#     st.image("./pass_map.jpg", caption="Pass Network Example", use_column_width=True)
#     # display image control in pitch
#     st.image("./pitch_zones_real.png", caption="Pitch Control Example", use_column_width=True)
#     return data