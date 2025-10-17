# ⚽ World Cup 2022 Football Analysis

A comprehensive interactive web application for analyzing FIFA World Cup 2022 matches, teams, and players using advanced football analytics and visualizations.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
  - [Match Analysis](#-match-analysis)
  - [Team Comparison](#-team-comparison)
  - [Player Analysis](#-player-analysis-in-development)
  - [Tournament Analysis](#-tournament-analysis-in-development)
- [Installation](#installation)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [Screenshots](#screenshots)
- [License](#license)

## Overview

This project provides an in-depth analysis of the FIFA World Cup 2022 through interactive visualizations and statistical insights. Built with Streamlit and Plotly, it offers football analysts, coaches, fans, and data enthusiasts a platform to explore match events, team performances, player statistics, and tournament progression.

The application processes event-level data including passes, shots, tackles, fouls, set pieces, and player movements to generate actionable insights and beautiful visualizations on a football pitch.

## Features

### ⚽ Match Analysis

**Status:** ✅ Complete

Analyze individual matches with comprehensive visualizations and statistics:

#### Basic Analysis
- **xG Timeline**: Track Expected Goals (xG) progression throughout the match for both teams
- **Tactical Analysis Radar**: Compare teams across multiple dimensions:
  - Possession percentage
  - Pass accuracy
  - Pressure events
  - Defensive actions
- **Match Statistics**: Detailed metrics including passes, shots, tackles, and more

#### Shot Analysis
- **Shot Map**: Interactive pitch visualization showing:
  - Shot locations with xG values (marker size represents xG)
  - Different markers for shot outcomes (Goal ⭐, Saved ⚪, Off Target ❌, Blocked ⬛)
  - Color-coded by team (Home: Blue, Away: Red)
  - Hover details showing player, xG value, and outcome
- **Shot Outcome Distribution**: Pie charts breaking down shot outcomes by team
- **Shot Statistics**: Comprehensive shot metrics and conversion rates

#### Advanced Features
- **Player Movement Heatmaps**: Visualize individual player activity zones across the pitch
- **Progressive Pass Analysis**: Track forward passes that significantly advance the ball
- **Set Piece Analysis**: Analyze corners, free kicks, and fouls with specialized markers:
  - Corners: Triangle markers
  - Free Kicks: Diamond markers
  - Fouls Committed: Circle markers
- **Pass Network**: Visualize team passing patterns and player connections

#### Multi-Match Comparison
- Compare up to 4 matches simultaneously side-by-side
- Filter matches by tournament stage (Group Stage, Round of 16, Quarter-finals, Semi-finals, Final)
- Dynamic add/remove comparison blocks

### 🏆 Team Comparison

**Status:** ✅ Complete

Compare two teams across their tournament performance:

#### Basic Analysis
- **Aggregate Statistics**: Average values from all team matches including:
  - Goals scored and conceded
  - Possession percentages
  - Pass accuracy
  - Shot statistics
  - xG metrics
  - Defensive actions
- **Tactical Radar Comparison**: Visual comparison of team styles
- **Performance Metrics**: Side-by-side statistical comparison

#### Shot Analysis
- **Combined Shot Map**: Visualize shots from both teams across all their matches
- **Comparative xG Analysis**: Compare shooting efficiency and quality
- **Shot Outcome Breakdown**: Detailed pie charts for each team

#### Multi-Team Comparison
- Compare up to 4 team pairs simultaneously
- Dynamic comparison blocks with add/remove functionality
- Comprehensive statistical breakdowns

### 👤 Player Analysis (In Development)

**Status:** 🚧 Coming Soon

Will include:
- Individual player performance metrics
- Player comparison tools
- Performance radar charts
- Tournament progression tracking
- Movement analysis and heat maps

### 🏅 Tournament Analysis (In Development)

**Status:** 🚧 Coming Soon

Will include:
- Overall tournament statistics
- Stage-by-stage progression
- Team rankings and performance
- Top players and moments
- Tournament trends and insights

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Required Packages

```bash
pip install streamlit
pip install pandas
pip install numpy
pip install plotly
pip install statsbombpy
```

Or install all at once:

```bash
pip install streamlit pandas numpy plotly statsbombpy
```

### Clone Repository

```bash
git clone https://github.com/yourusername/worldcup-2022-analysis.git
cd worldcup-2022-analysis
```

## Usage

1. **Start the Application**

```bash
streamlit run main.py
```

2. **Navigate the Application**
   - The home page provides an overview and navigation to different sections
   - Use the sidebar to switch between analysis types
   - Select matches, teams, or players from dropdown menus
   - Interact with visualizations (hover, zoom, pan)

3. **Match Analysis**
   - Select a tournament stage to filter matches
   - Choose a specific match from the dropdown
   - Switch between different analysis tabs (Basic, Shot, Movement, etc.)
   - Add multiple match comparison blocks using the ➕ button

4. **Team Comparison**
   - Select two teams to compare
   - Choose between Basic Analysis and Shot Analysis
   - View aggregate statistics from all team matches
   - Add multiple comparison blocks for different team pairs

## Data Sources

This application supports two data sources:

### 1. StatsBomb Open Data (Primary)
- Accessed via the `statsbombpy` Python library
- Provides comprehensive event-level data for World Cup 2022
- Automatically fetched when available
- Includes detailed event information: locations, timestamps, outcomes, xG values

### 2. Local JSON Files (Backup/Supplement)
- Located in `world_cup_data/` directory
- `shot_map_data.json`: Shot event data for all teams
- Used for team comparison analysis
- Fallback when StatsBomb API is unavailable

The application intelligently switches between data sources based on availability and analysis type.

## Screenshots

To showcase your project, add the following screenshots to a `screenshots/` folder in your repository:

### Recommended Screenshots:

1. **`screenshots/home.png`** - Main landing page showing the project overview

2. **`screenshots/match-analysis-basic.png`** - Match analysis with xG timeline and tactical radar

3. **`screenshots/match-shot-map.png`** - Interactive shot map showing both teams' shots with xG values

4. **`screenshots/player-heatmap.png`** - Player movement heatmap on the pitch

5. **`screenshots/progressive-passes.png`** - Progressive passing analysis with arrows

6. **`screenshots/set-pieces.png`** - Set piece analysis with different markers

7. **`screenshots/team-comparison.png`** - Side-by-side team comparison with statistics

8. **`screenshots/multi-match.png`** - Multiple match comparison blocks in action

### How to Add Screenshots:

After adding screenshots, update this section with:

```markdown
### Home Page
![Home Page](screenshots/home.png)

### Match Analysis - Shot Map
![Shot Map](screenshots/match-shot-map.png)

### Player Heatmap
![Player Heatmap](screenshots/player-heatmap.png)

### Team Comparison
![Team Comparison](screenshots/team-comparison.png)
```

## Technical Highlights

- **Interactive Visualizations**: Built with Plotly for smooth, interactive charts and pitch visualizations
- **Real Football Pitch**: Accurate pitch dimensions (120x80) with penalty areas, goals, and center circle
- **Event Processing**: Sophisticated event data preprocessing and aggregation
- **Multiple Views**: Compare up to 4 matches or team pairs simultaneously
- **Responsive Design**: Clean UI with custom CSS styling
- **Performance**: Caching mechanisms for fast data loading
- **Modular Architecture**: Separated analysis modules for maintainability

## Project Structure

```
worldcup-2022-analysis/
├── main.py                    # Main application entry point
├── Base.py
├── README.md
├── analysis
│   ├── FootballDataLoader.py
│   ├── __init__.py
│   └── worldcup_to_csv.py   
├── data
│   ├── Team_comparison.csv  
│   ├── explain_json_data.png
│   ├── matches_index.csv
│   ├── shot_map_data.json
│   └── worldcup_2022_match_data.csv
├── football-EDA
├── frontend
│   ├── Match_tabs
│   │   ├── Base.py
│   │   ├── Basic_Analysis.py
│   │   ├── Basic_tabs
│   │   │   ├── attack_tab.py
│   │   │   ├── basic_tab.py
│   │   │   ├── defensive_tab.py
│   │   │   ├── efficiency_tab.py
│   │   │   ├── goalkeeper_tab.py
│   │   │   ├── pass_analysis.py
│   │   │   ├── plot_tmp.py
│   │   │   ├── team_shape_tab.py
│   │   │   └── transition_tab.py
│   │   ├── Movement_analysis.py
│   │   ├── Pass_analysis.py
│   │   ├── Progressive_play.py
│   │   ├── Set_piece.py
│   │   ├── Shot_analysis.py
│   │   ├── Shot_analysis_tmp.py
│   ├── __init__.py
│   ├── helpers
│   │   ├── __init__.py
│   │   └── page_cfg.py
│   ├── main.py
│   └── pages
│       ├── Match_Analysis.py
│       ├── Team Comparison.py
│       ├── __init__.py
│       ├── data.py
│       ├── football-EDA
│       └── player Comparison.py
├── requirements.txt
```

## License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Acknowledgments

- **StatsBomb** for providing open football data
- **Streamlit** for the web application framework
- **Plotly** for interactive visualizations

## Support

For issues, questions, or suggestions, please open an issue on GitHub or communicate with us on LinkedIn.

---

**Note**: This is an educational project for football analytics and data visualization. All data is used for non-commercial, analytical purposes.
