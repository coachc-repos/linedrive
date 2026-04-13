#!/usr/bin/env python3
"""
Emotional Thumbnail Generator for YouTube Videos
Generates 6 variations with different emotional expressions using Google Gemini Flash Image
"""

import os
import re
from io import BytesIO
from pathlib import Path
from datetime import datetime
from PIL import Image

# Lazy import for google.generativeai - only import when needed
# This gives better error messages and avoids import-time failures
_genai = None


def _ensure_genai():
    """Lazy import of google.generativeai with helpful error message"""
    global _genai
    if _genai is None:
        try:
            import google.generativeai as genai
            _genai = genai
        except ImportError as e:
            raise ImportError(
                "google-generativeai package is required for thumbnail generation.\n"
                "Install it with: pip install google-generativeai\n"
                f"Original error: {e}"
            )
    return _genai


class EmotionalThumbnailGenerator:
    """Generate emotional thumbnail variations using Google Gemini Flash Image"""

    def __init__(self, api_key=None, template_path=None, output_dir=None):
        """
        Initialize the thumbnail generator

        Args:
            api_key: Google API key (defaults to env var GOOGLE_API_KEY)
            template_path: Path to template image (defaults to thumbnail_template_canva.png)
            output_dir: Output directory for thumbnails (defaults to ~/Dev/Thumbnails)
        """
        self.api_key = api_key or os.getenv(
            "GOOGLE_API_KEY", "AIzaSyAiFFlgDokz-s4U8UrV73Fhdnl8Ukx2jCM")

        # Use absolute path for template - find it relative to this file
        if template_path:
            self.template_path = template_path
        else:
            current_dir = Path(__file__).parent
            self.template_path = str(
                current_dir / "Thumbnail_Template_Canva.png")

        self.output_dir = Path(
            output_dir or os.path.expanduser("~/Dev/Thumbnails"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configure Gemini API (lazy import)
        genai = _ensure_genai()
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

    def extract_thumbnail_text_from_upload_details(self, upload_details):
        """
        Extract thumbnail text suggestions from YouTube upload details

        Args:
            upload_details: String containing YouTube upload details markdown

        Returns:
            String with primary thumbnail text suggestion, or None
        """
        if not upload_details:
            return None

        # Look for thumbnail text section
        thumbnail_section = re.search(
            r'## 🖼️ THUMBNAIL TEXT\s*\n(.*?)(?=\n##|\Z)',
            upload_details,
            re.DOTALL | re.IGNORECASE
        )

        if thumbnail_section:
            text = thumbnail_section.group(1).strip()
            # Extract first suggestion (usually the most prominent)
            lines = [line.strip() for line in text.split(
                '\n') if line.strip() and not line.strip().startswith('-')]
            if lines:
                # Clean up formatting
                suggestion = lines[0].strip('"').strip("'").strip()
                return suggestion

        return None

    def generate_emotional_variations(self, base_text=None):
        """
        Generate 6 emotional variation configurations

        Args:
            base_text: Optional base text to derive emotions from

        Returns:
            List of dicts with emotion configs
        """
        variations = [
            {
                "emotion": "ANGRY/FRUSTRATED",
                "thumbnail_text": "THIS IS RIDICULOUS!" if not base_text else f"{base_text.upper()}!",
                "expression": "angry and frustrated, furrowed brows, intense stare",
                "mood": "confrontational and challenging",
                "outfit": "black leather jacket with edgy accessories",
                "background": "Dark industrial setting with dramatic red lighting and steam"
            },
            {
                "emotion": "SHOCKED/SURPRISED",
                "thumbnail_text": "WAIT... WHAT?!" if not base_text else f"WAIT... {base_text.upper()}?!",
                "expression": "shocked and surprised, wide eyes, mouth open",
                "mood": "disbelief and amazement",
                "outfit": "trendy oversized blazer with modern streetwear",
                "background": "Bright modern office with holographic displays and bright blue tones"
            },
            {
                "emotion": "SCARED/WORRIED",
                "thumbnail_text": "YOU'RE IN DANGER" if not base_text else f"{base_text.upper()} - DANGER!",
                "expression": "concerned and worried, raised eyebrows, serious look",
                "mood": "warning and urgency",
                "outfit": "tactical vest with streetwear elements",
                "background": "Moody purple-blue cyberpunk cityscape with neon signs"
            },
            {
                "emotion": "EXCITED/ENERGETIC",
                "thumbnail_text": "THIS CHANGES EVERYTHING!" if not base_text else f"{base_text.upper()} IS HERE!",
                "expression": "excited and energetic, wide smile, enthusiastic",
                "mood": "enthusiasm and breakthrough",
                "outfit": "vibrant current fashion with bold colorful patterns",
                "background": "Bright futuristic laboratory with green and yellow lighting"
            },
            {
                "emotion": "SKEPTICAL/DOUBTFUL",
                "thumbnail_text": "I DON'T BELIEVE IT" if not base_text else f"IS {base_text.upper()} REAL?",
                "expression": "skeptical and doubtful, raised eyebrow, smirk",
                "mood": "questioning and analytical",
                "outfit": "chic contemporary designer outfit",
                "background": "Sleek minimalist tech studio with cool teal tones"
            },
            {
                "emotion": "DETERMINED/INTENSE",
                "thumbnail_text": "HERE'S THE TRUTH" if not base_text else f"{base_text.upper()} - THE TRUTH",
                "expression": "determined and intense, direct eye contact, serious",
                "mood": "authoritative and confident",
                "outfit": "dark tactical futuristic gear",
                "background": "Dramatic server room with green matrix-style lighting"
            }
        ]

        return variations

    def generate_thumbnail_variation(self, script_title, emotion_data, variation_num):
        """
        Generate a single thumbnail variation

        Args:
            script_title: Title/topic of the video script
            emotion_data: Dict with emotion, expression, outfit, background info
            variation_num: Variation number (1-6)

        Returns:
            PIL Image object or None on failure
        """
        # Load template image
        template_img = Image.open(self.template_path)

        # Create detailed prompt for model
        prompt = f"""You are modifying a YouTube thumbnail template image (1280x720 aspect ratio).

TEMPLATE IMAGE PROVIDED: This image shows a person in a specific pose pointing upward.

CRITICAL INSTRUCTIONS - WHAT TO PRESERVE:
1. KEEP THE PERSON'S POSE, BODY POSITION, AND POINTING ARM EXACTLY AS IS - DO NOT CHANGE
2. Keep the person's size and placement in the frame EXACTLY as shown
3. Keep the arm gesture and pointing direction EXACTLY as shown
4. Keep the overall composition EXACTLY as shown

WHAT TO TRANSFORM (ONLY 3 THINGS):
1. BACKGROUND: Replace white/plain background with colorful futuristic scene
2. FACIAL EXPRESSION: Transform the person's face to match emotion
3. OUTFIT: Change what the person is wearing

DO NOT ADD ANY TEXT OR WORDS TO THE IMAGE.

BACKGROUND REPLACEMENT:
Topic: {script_title}
Specific Background: {emotion_data['background']}
- Replace the current background with a COLORFUL, FUTURISTIC scene
- Background must relate to: {script_title}
- Background should be: {emotion_data['background']}
- MANDATORY: Background fills ENTIRE frame edge-to-edge (1280x720)
- High resolution, detailed, vibrant colors
- Futuristic tech aesthetic with rich visual detail
- Dramatic lighting that complements the scene
- Background should be prominent in UPPER LEFT where text will go
- Ensure background extends to all edges with no white space
- Create DISTINCTLY DIFFERENT backgrounds for each variation

FACIAL EXPRESSION CHANGE:
- Transform ONLY the person's face to show: {emotion_data['expression']}
- Make expression EXAGGERATED and CLEAR for thumbnail visibility
- Expression must convey: {emotion_data['mood']}
- Emotion: {emotion_data['emotion']}
- Keep face proportional and natural
- DO NOT change head position or angle, only facial expression
- Face should match the emotion while maintaining the pose

OUTFIT CHANGE:
- Change clothing to: {emotion_data['outfit']}
- Mix of edgy fashion AND current trendy styles
- Make outfit stylish, modern, and fashionable
- Should look current and contemporary
- Keep outfit appropriate for thumbnail visibility

COLOR PALETTE for backgrounds:
- ANGRY: Reds, oranges, dark dramatic (#ef4444, #dc2626, #1e293b)
- SHOCKED: Bright blues, whites, high contrast (#ffffff, #0ea5e9, #38bdf8)
- SCARED: Dark blues, purples, moody (#1e293b, #7c3aed, #dc2626)
- EXCITED: Vibrant yellows, greens, energetic (#fbbf24, #22c55e, #0ea5e9)
- SKEPTICAL: Cool grays, teals, modern (#64748b, #06b6d4, #475569)
- DETERMINED: Deep reds, blacks, powerful (#991b1b, #1f2937, #b91c1c)

FINAL OUTPUT REQUIREMENTS:
- 1280x720 pixels, 16:9 aspect ratio
- Person in SAME POSITION as template with pointing gesture UNCHANGED
- NEW colorful futuristic background filling entire frame
- NEW facial expression matching emotion
- NEW outfit matching style description
- NO TEXT on image
- High visual impact, professional quality
- Background extends to all edges with no gaps

Style: HIGH RESOLUTION photorealistic, preserve original pose and gesture exactly, colorful futuristic backgrounds, varied facial expressions, contemporary fashion, YouTube thumbnail optimized."""

        try:
            # Generate image with Gemini
            response = self.model.generate_content([prompt, template_img])

            # Extract image from response
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        img = Image.open(BytesIO(part.inline_data.data))

                        # Ensure correct dimensions
                        if img.size != (1280, 720):
                            img = img.resize(
                                (1280, 720), Image.Resampling.LANCZOS)

                        return img

            print(
                f"⚠️ No image data in response for variation {variation_num}")
            return None

        except Exception as e:
            print(f"❌ Error generating variation {variation_num}: {e}")
            return None

    def generate_all_thumbnails(self, script_title, script_content=None, youtube_upload_details=None):
        """
        Generate all 6 thumbnail variations

        Args:
            script_title: Title/topic of the video
            script_content: Optional script content for context
            youtube_upload_details: Optional YouTube upload details with thumbnail text

        Returns:
            Dict with variation info and file paths
        """
        # Extract thumbnail text from upload details if available
        base_text = None
        if youtube_upload_details:
            base_text = self.extract_thumbnail_text_from_upload_details(
                youtube_upload_details)

        # Generate emotional variations
        variations = self.generate_emotional_variations(base_text)

        # Create safe filename
        safe_title = re.sub(
            r'[^\w\s-]', '', script_title).strip().replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        results = {
            "script_title": script_title,
            "base_text": base_text,
            "variations": [],
            "output_dir": str(self.output_dir)
        }

        print(f"\n{'='*70}")
        print(f"🎬 Generating 6 Emotional Thumbnails: '{script_title}'")
        print(f"📸 Template: {self.template_path}")
        if base_text:
            print(f"💬 Base Text: {base_text}")
        print(f"{'='*70}\n")

        for i, emotion_data in enumerate(variations, 1):
            print(f"{'─'*70}")
            print(f"🎭 Variation #{i}")
            print(f"   Emotion: {emotion_data['emotion']}")
            print(f"   Text: {emotion_data['thumbnail_text']}")
            print(f"   Expression: {emotion_data['expression']}")

            # Generate thumbnail
            img = self.generate_thumbnail_variation(
                script_title, emotion_data, i)

            if img:
                # Save file
                filename = f"{safe_title}_v{i}_{timestamp}.png"
                filepath = self.output_dir / filename
                img.save(filepath, "PNG", quality=95)

                print(f"   ✅ Generated: {img.size}")
                print(f"   💾 Saved: {filename}\n")

                results["variations"].append({
                    "number": i,
                    "emotion": emotion_data['emotion'],
                    "text": emotion_data['thumbnail_text'],
                    "expression": emotion_data['expression'],
                    "outfit": emotion_data['outfit'],
                    "background": emotion_data['background'],
                    "filename": filename,
                    "filepath": str(filepath),
                    "dimensions": img.size
                })
            else:
                print(f"   ❌ Failed to generate\n")

        return results

    def display_summary(self, results):
        """Display a summary of generated thumbnails"""
        print(f"\n{'='*70}")
        print(f"✅ EMOTIONAL THUMBNAIL GENERATION COMPLETE")
        print(f"{'='*70}\n")
        print(f"📁 Output Directory: {results['output_dir']}\n")

        if results.get('base_text'):
            print(f"💬 Base Text Used: {results['base_text']}\n")

        for var in results['variations']:
            print(f"{'─'*70}")
            print(f"🎭 Variation #{var['number']}: {var['emotion']}")
            print(f"   Text: {var['text']}")
            print(
                f"   Dimensions: {var['dimensions'][0]}x{var['dimensions'][1]}")
            print(f"   File: {var['filename']}")

        print(f"{'─'*70}\n")
        print(f"💡 Next Steps:")
        print(f"   1. Review thumbnails - person should have transformed expressions")
        print(f"   2. Open in Canva to add text overlay on LEFT side")
        print(f"   3. Use the suggested text for each variation")
        print(f"   4. Export final thumbnails")


def main():
    """Test harness for standalone usage"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate emotional thumbnail variations using Google Gemini"
    )
    parser.add_argument(
        "--template",
        default="tools/media/thumbnail_template_canva.png",
        help="Path to template image"
    )
    parser.add_argument(
        "--script",
        help="Path to script markdown file"
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Video title/topic"
    )
    parser.add_argument(
        "--youtube-details",
        help="Path to YouTube upload details file"
    )
    parser.add_argument(
        "--output",
        help="Output directory for thumbnails"
    )

    args = parser.parse_args()

    # Load script content if provided
    script_content = None
    if args.script:
        with open(args.script, 'r', encoding='utf-8') as f:
            script_content = f.read()

    # Load YouTube details if provided
    youtube_details = None
    if args.youtube_details:
        with open(args.youtube_details, 'r', encoding='utf-8') as f:
            youtube_details = f.read()

    # Create generator
    generator = EmotionalThumbnailGenerator(
        template_path=args.template,
        output_dir=args.output
    )

    # Generate thumbnails
    results = generator.generate_all_thumbnails(
        script_title=args.title,
        script_content=script_content,
        youtube_upload_details=youtube_details
    )

    # Display summary
    generator.display_summary(results)


if __name__ == "__main__":
    main()
