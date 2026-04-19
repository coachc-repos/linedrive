# 📚 LineDrive - AI-Powered Content Creation & Baseball Data Platform

**Version 2.0.0** | [Full Documentation](DOCUMENTATION.md)

A comprehensive multi-module platform combining AI-powered YouTube script creation, emotional thumbnail generation, and baseball tournament data management.

## � Quick Start

### YouTube Script Creation (Primary Feature)

**Console UI** (Fastest - 3 minutes):
```bash
python console_launcher_modular.py
# Select: 2. 🎬 Full Script Creation Workflow
```

**Web GUI** (Visual Interface):
```bash
cd scriptcraft-app
python web_gui.py
# Open: http://localhost:8080
```

### Emotional Thumbnail Generation

```bash
# Standalone test
python tools/test_emotional_thumbnails.py

# Integrated in workflow (automatic at Step 4.8)
# Generates 6 AI-powered variations using Gemini Flash Image
```

### Baseball Tournament Data

```bash
cd batch_scrapers
python batch_scraper_ui.py
# Options: Perfect Game scraping, YouTube transcripts, Azure storage
```

## 🎯 Core Capabilities

| Feature | Description | Entry Point |
|---------|-------------|-------------|
| **🎬 Script Creation** | AI-powered 4-agent workflow for YouTube scripts | `console_launcher_modular.py` |
| **🎨 Thumbnails** | 6 emotional variations with Gemini AI | `tools/media/emotional_thumbnail_generator.py` |
| **⚾ Baseball Data** | Multi-league tournament scraping + Azure storage | `batch_scrapers/batch_scraper_ui.py` |
| **📱 Social Media** | X/Twitter integration for content distribution | `social_media/` |
| **☁️ Azure Deploy** | Container Apps + Static Web Apps | `scriptcraft-app/` |

## 📖 Documentation

**📘 [DOCUMENTATION.md](DOCUMENTATION.md)** - Complete system documentation including:
- Architecture & design patterns
- Module descriptions & API reference
- Development guide & best practices
- Deployment instructions
- Troubleshooting guide

## �️ Project Structure

```
linedrive/
├── 🎬 ScriptCraft System
│   ├── console_launcher_modular.py    # Primary console entry
│   ├── console_ui/                    # UI modules
│   └── scriptcraft-app/               # Web GUI + Azure deployment
│
├── 🤖 AI Agents
│   └── linedrive_azure/agents/
│       ├── enhanced_autogen_system.py # 4-agent workflow
│       ├── script_writer_agent_client.py
│       ├── script_review_agent_client.py
│       └── youtube_upload_details_agent_client.py
│
├── 🎨 Media Generation
│   └── tools/media/
│       ├── emotional_thumbnail_generator.py  # ✨ NEW v2.0
│       └── thumbnail_generator.py            # Legacy
│
├── ⚾ Baseball Data
│   ├── batch_scrapers/                # Tournament scraping
│   ├── scraper/                       # Multi-league support
│   └── linedrive_azure/storage/       # Azure Data Lake
│
└── 📱 Social Media
    └── social_media/                  # X/Twitter integration
```

## 🔧 Prerequisites

```bash
# Python 3.12
python --version  # Must be 3.12.x

# Virtual environment
source venv314/bin/activate

# Install dependencies
pip install -r requirements.txt

# Azure CLI (for authentication)
az login
```

## 🎨 What's New in v2.0.0

### Emotional Thumbnail Generator
- **6 AI-powered variations**: ANGRY, SHOCKED, SCARED, EXCITED, SKEPTICAL, DETERMINED
- **Gemini Flash Image API**: Advanced AI transformations
- **Template preservation**: Maintains pose while transforming background/expression
- **Auto-integration**: Generates at Step 4.8 in script workflow
- **Quick testing**: `python tools/test_emotional_thumbnails.py`

### Improvements
- ✅ Lazy loading for better import performance
- ✅ 15-minute timeout for complex script chapters
- ✅ Enhanced logging and progress indicators
- ✅ Consolidated documentation

## 📝 Example Usage

### Complete Script Workflow
```bash
# Console (interactive)
python console_launcher_modular.py

# Inputs:
# - Topic: "AI at Home is a Must"
# - Audience: general
# - Tone: conversational
# - Length: short (3-5 min)

# Outputs:
# ✅ Complete script (Word + Markdown)
# ✅ YouTube upload details
# ✅ 6 thumbnail variations
# ✅ B-roll suggestions
```

### Thumbnail Generation Only
```python
from tools.media.emotional_thumbnail_generator import EmotionalThumbnailGenerator

gen = EmotionalThumbnailGenerator()
results = gen.generate_all_thumbnails(
    script_title="Your Title",
    script_content="Your script...",
    youtube_upload_details="## 🖼️ THUMBNAIL TEXT\nYour text..."
)
```

## � Deployment

### Azure Container Apps
```bash
cd scriptcraft-app
docker build -t linedrive-scriptcraft .
az containerapp create --name linedrive-scriptcraft ...
```

### Azure Static Web Apps
```bash
cd web
az staticwebapp create --name linedrive-web ...
```

See [DOCUMENTATION.md](DOCUMENTATION.md) for complete deployment instructions.

## 🐛 Troubleshooting

### Common Issues

**Import Error: `google.generativeai`**
```bash
pip install google-generativeai
```

**Wrong Python/venv**
```bash
# Use venv314 explicitly
venv314/bin/python console_launcher_modular.py
```

**Console UI errors**
```bash
# Always run from project root
cd /Users/christhi/Dev/Github/linedrive
python console_launcher_modular.py
```

See [DOCUMENTATION.md - Troubleshooting](DOCUMENTATION.md#troubleshooting) for more.

## 🏷️ Version History

- **v2.0.0** (Oct 2025) - Emotional Thumbnails + Gemini AI integration
- **v1.5.24** (Oct 2025) - Tone selector + Technical levels
- **v1.0** - Working Web GUI baseline

## 📞 Support

- **📘 Full Docs**: [DOCUMENTATION.md](DOCUMENTATION.md)
- **🐛 Issues**: GitHub Issues
- **📧 Contact**: Christian Thilmany

---

**© 2025 LineDrive Project**

All scraped data is automatically uploaded to Azure Data Lake:

- **Storage Account:** `linedrivestorage`
- **Container:** `tournament-data`
- **Path Structure:** `raw/year=YYYY/month=MM/day=DD/`
- **Authentication:** Azure CLI credentials

## 📚 Detailed Documentation

### Batch Scrapers System

#### YouTube Transcript Module

**Purpose:** Extract, process, and store YouTube video transcripts with Azure integration.

**Key Features:**

- **Multi-language support:** Handles various transcript languages (en, en-US, etc.)
- **Full-text generation:** Creates continuous readable text from timestamped entries
- **Azure integration:** Automatic uploads to Data Lake storage
- **Interactive menu:** Comprehensive viewing and export options
- **Error handling:** Robust handling of missing transcripts and API failures

**Data Structure:**
```json
{
  "metadata": {
    "fetched_at": "2025-08-12T16:34:57.189973",
    "total_entries": 610,
    "total_duration": 1276.549
  },
  "full_text": "Complete continuous transcript text...",
  "transcript": [
    {
      "text": "Individual transcript segment",
      "start": 0.96,
      "duration": 4.08
    }
  ]
}
```

#### Perfect Game Tournament Scraper

**Purpose:** Collect tournament data from Perfect Game website with advanced filtering.

**Key Methods:**

- **`fetch_youtube_transcript(video_id, languages)`**
  - **Purpose:** Extract transcript data from YouTube videos
  - **Parameters:**
    - `video_id`: YouTube video ID (e.g., 'NgF2G9VItKY')
    - `languages`: List of language codes to attempt
  - **Returns:** List of transcript entries or None if failed
  - **Error Handling:** Comprehensive handling of disabled/missing transcripts

- **`save_transcript_to_json(transcript, output_path)`**
  - **Purpose:** Save transcript with metadata in enhanced JSON format
  - **Features:** Metadata generation, full-text creation, timestamp processing
  - **Output:** Both timestamped entries and continuous readable text

### Azure Data Lake Storage Module

**Purpose:** Centralized cloud storage for all scraped data with proper organization.

**Key Methods:**

- **`upload_raw_data(data, run_type)`**
  - **Purpose:** Upload raw data as JSON with automatic metadata
  - **Organization:** `raw/year=YYYY/month=MM/day=DD/tournaments_YYYYMMDD_HHMMSS.json`
  - **Features:** Automatic partitioning, metadata enrichment, error handling

- **`test_connection()`**
  - **Purpose:** Verify Azure Data Lake connectivity and authentication
  - **Returns:** Boolean success status with detailed logging

**Authentication:** Uses ChainedTokenCredential with Azure CLI priority

**Storage Pattern:**
- **Container:** `tournament-data`
- **Raw Data:** `raw/year=YYYY/month=MM/day=DD/`
- **Processed Data:** `processed/year=YYYY/month=MM/day=DD/`

### AutoGen Multi-Agent System

**Purpose:** AI-powered tournament planning with specialized agent collaboration.

**Agents:**
- **TournamentFinder:** Searches and filters tournament data
- **TournamentPlanner:** Creates tournament recommendations
- **TournamentAdvisor:** Provides strategic tournament advice

**Integration:**
- **Azure AI:** Connected to Azure OpenAI services
- **Grok API:** Alternative LLM backend for redundancy
- **Data Sources:** Real-time Perfect Game scraping + Azure search

## 🛠️ Development Setup

### Prerequisites

```bash
# Python 3.11+ required
python --version

# Install dependencies
pip install -r requirements.txt
```

### Azure Configuration

```bash
# Install Azure CLI
# Login to Azure
az login

# Verify access to storage account
az storage account show --name linedrivestorage --resource-group rg-linedrive-storage
```

### Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd linedrive

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 📖 Usage Examples

### Batch Scraping Workflow

```bash
# Start batch scraper interface
cd batch_scrapers
python batch_scraper_ui.py

# Select Perfect Game scraper (Option 1)
# Configure filters and run scraping
# Data automatically uploads to Azure Data Lake
```

### YouTube Transcript Extraction

```bash
# Start batch scraper interface
cd batch_scrapers
python batch_scraper_ui.py

# Select YouTube Transcript (Option 3)
# Enter video URL or ID
# Enable Azure upload in settings
# View transcript and export options
```

### AutoGen Tournament Planning

```bash
# Start AutoGen interface
python autogen_tournament_ui.py

# Select agents and configure backends
# Enter tournament requirements
# Get AI-powered recommendations
```

## 🗂️ Data Storage Structure

### Azure Data Lake Organization

```text
tournament-data/
├── raw/
│   └── year=2025/
│       └── month=08/
│           └── day=12/
│               ├── tournaments_20250812_163457.json
│               └── tournaments_20250812_164523.json
└── processed/
    └── year=2025/
        └── month=08/
            └── day=12/
                └── tournaments_20250812_163457.csv
```

### Local Output Directory

```text
output/
├── youtube_transcript_<video_id>_<timestamp>.json
├── tournament_results_<timestamp>.json
└── scraper_logs_<timestamp>.log
```

## 🔧 Configuration

### Azure Storage Settings

- **Storage Account:** `linedrivestorage`
- **Resource Group:** `rg-linedrive-storage`
- **Authentication:** Azure CLI credentials (ChainedTokenCredential)
- **Container:** `tournament-data`

### YouTube Transcript Settings

- **Default Languages:** `['en', 'en-US']`
- **Output Format:** Enhanced JSON with full_text field
- **Azure Upload:** Configurable via menu settings

### Perfect Game Scraper Settings

- **Base URL:** `https://www.perfectgame.org/`
- **Rate Limiting:** Built-in delays to respect site limits
- **Error Handling:** Comprehensive retry logic

## 📋 Recent Updates

- ✅ **Enhanced YouTube Transcript System** - Full-text continuous transcript generation
- ✅ **Azure Data Lake Integration** - Automatic uploads with proper authentication
- ✅ **Batch Scraper UI** - Unified interface for all scraping operations
- ✅ **Error Handling** - Comprehensive error handling and logging
- ✅ **Data Structure** - Standardized JSON output with metadata
- ✅ **Menu System** - Interactive configuration and settings management

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For issues and questions:

- Check the error logs in the `output/` directory
- Verify Azure CLI authentication: `az account show`
- Test Azure connectivity in batch scraper settings menu


