import os
import re
import aiohttp
import aiofiles
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL


async def gen_thumb(videoid):
    """Get YouTube thumbnail and create custom design"""
    try:
        query = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(query, limit=1)
        
        for result in (await results.next())["result"]:
            title = result.get("title", "Unknown Title")
            channel = result.get("channel", {}).get("name", "Unknown")
            duration = result.get("duration", "00:00")
            views = result.get("viewCount", {}).get("short", "0")
            thumbnail_url = result["thumbnails"][0]["url"].split("?")[0]
            
            # Download and create custom thumbnail
            custom_thumb = await create_custom_thumbnail(
                thumbnail_url, 
                title, 
                channel, 
                duration,
                views,
                videoid
            )
            return custom_thumb
    except Exception as e:
        print(f"Error in get_thumb: {e}")
        return YOUTUBE_IMG_URL


async def gen_qthumb(vidid):
    """Quick thumbnail fetch without customization"""
    try:
        query = f"https://www.youtube.com/watch?v={vidid}"
        results = VideosSearch(query, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail
    except Exception as e:
        return YOUTUBE_IMG_URL


async def download_image(url, path):
    """Download image from URL"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(path, mode='wb')
                await f.write(await resp.read())
                await f.close()


def create_rounded_mask(size, radius):
    """Create a rounded corner mask"""
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), size], radius=radius, fill=255)
    return mask


async def create_custom_thumbnail(thumbnail_url, title, channel, duration, views, videoid):
    """Create thumbnail matching the reference 'Classy' design"""
    
    project_root = "TNC_MUSIC/"
    temp_dir = os.path.join(project_root, "temp")
    assets_dir = os.path.join(project_root, "assets")
    
    if not os.path.isdir(temp_dir):
        os.makedirs(temp_dir)
    
    temp_thumb = f"{temp_dir}/thumb_{videoid}.jpg"
    final_thumb = f"{temp_dir}/final_{videoid}.jpg"
    
    try:
        await download_image(thumbnail_url, temp_thumb)
        
        # Open original image
        original_img = Image.open(temp_thumb).convert("RGBA")
        
        # Create canvas
        canvas_width = 1280
        canvas_height = 720
        canvas = Image.new('RGB', (canvas_width, canvas_height), (0, 0, 0))
        
        # === 1. BLURRED BACKGROUND (More visible) ===
        bg_img = original_img.copy().resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=22))
        enhancer = ImageEnhance.Brightness(bg_img)
        bg_img = enhancer.enhance(0.61)  # Semi-visible background
        canvas.paste(bg_img, (0, 0))

        # === 2. FROSTED GLASS PANEL (LARGER) ===
        # panel_width = 500
        # panel_height = 320
        # panel_x = (canvas_width - panel_width) // 2
        # panel_y = 105
        
        # # Create glass effect - blend with background
        # glass_base = canvas.crop((panel_x, panel_y, panel_x + panel_width, panel_y + panel_height))
        # glass_base = glass_base.filter(ImageFilter.GaussianBlur(radius=12))
        
        # # Lighten slightly for glass effect
        # enhancer = ImageEnhance.Brightness(glass_base)
        # glass_base = enhancer.enhance(1.25)
        
        # # Convert to RGBA and add subtle transparency
        # glass_base = glass_base.convert('RGBA')
        # overlay = Image.new('RGBA', (panel_width, panel_height), (255, 255, 255, 35))
        # glass_base = Image.alpha_composite(glass_base, overlay)
        
        # # Apply rounded mask
        # panel_mask = create_rounded_mask((panel_width, panel_height), radius=32)
        # canvas.paste(glass_base, (panel_x, panel_y), panel_mask)
        
        # === 3. MAIN THUMBNAIL (LARGER) ===
        thumb_width = 485
        thumb_height = 305
        thumb_x = (canvas_width - thumb_width) // 2
        thumb_y = 110
        
        thumb_display = original_img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        thumb_mask = create_rounded_mask((thumb_width, thumb_height), radius=30) 
        canvas.paste(thumb_display, (thumb_x, thumb_y), thumb_mask)

        # === 4. LOAD FONTS ===
        draw = ImageDraw.Draw(canvas)
        font_path = os.path.join(project_root, "assets", "font.ttf")
        font2_path = os.path.join(project_root, "assets", "font2.ttf")
        
        try:
            title_font = ImageFont.truetype(font_path, 38)
            duration_font = ImageFont.truetype(font2_path, 20) # For fallback player
            bottom_duration_font = ImageFont.truetype(font_path, 24) # Bolder/Larger
            watermark_font = ImageFont.truetype(font_path, 28)
        except Exception as e:
            print(f"Font loading error: {e}")
            title_font = ImageFont.load_default()
            duration_font = ImageFont.load_default()
            bottom_duration_font = ImageFont.load_default() 
            watermark_font = ImageFont.load_default()

        # === 5. DURATION BADGE (REMOVED) ===
        # This section is intentionally left blank as requested.

        # === 6. WATERMARK (Top-right) ===
        watermark_text = "Classy"
        draw.text((canvas_width - 150, 35), watermark_text, fill=(255, 255, 255), font=watermark_font)

        # === 7. TITLE (Below Panel) ===
        title_y = thumb_y + thumb_height + 40
        
        # Clean title and crop if needed
        title = clean_text(title)
        if len(title) > 30:
            title = title[:27] + "..."
        
        # Draw centered title
        draw.text((canvas_width // 2, title_y), title, fill=(255, 255, 255), font=title_font, anchor="mt")

        # === 8. DURATION TEXT (Below Title, Bolder/Larger) ===
        duration_y = title_y + 60
        draw.text((canvas_width // 2, duration_y), duration, fill=(200, 200, 200), font=bottom_duration_font, anchor="mt")

        # === 9. PLAYER CONTROLS IMAGE (Smaller, Down, Semi-Transparent, Rounded) ===
        player_img_path = os.path.join(assets_dir, "player.png")
        
        # Try both .png and .jpg extensions
        if not os.path.exists(player_img_path):
            player_img_path = os.path.join(assets_dir, "player.jpg")
        
        if os.path.exists(player_img_path):
            try:
                player_img = Image.open(player_img_path).convert("RGBA")
                
                # CHANGED: Resize player to be smaller
                player_width = 380 # Was 400
                player_height = int(player_img.height * (player_width / player_img.width))
                player_img = player_img.resize((player_width, player_height), Image.Resampling.LANCZOS)
                
                # Position at bottom
                player_x = (canvas_width - player_width) // 2
                player_y = 570 # CHANGED: Was 550, moved down
                
                # Create semi-transparent version
                transparent_player = Image.new("RGBA", player_img.size, (0, 0, 0, 0))
                transparent_player = Image.blend(transparent_player, player_img, 0.75) # 75% opacity

                # Create rounded mask for the player image
                player_mask = create_rounded_mask(player_img.size, radius=38)

                # Paste with transparency AND rounded mask
                canvas.paste(transparent_player, (player_x, player_y), player_mask)
            except Exception as e:
                print(f"Error loading player image: {e}")
                # Fallback: draw basic player controls
                draw_fallback_player(draw, canvas_width, duration_font, 570, 380) # Pass new Y and Width
        else:
            print("Player image not found, using fallback")
            # Fallback: draw basic player controls
            draw_fallback_player(draw, canvas_width, duration_font, 570, 380) # Pass new Y and Width
        
        # === 10. SAVE FINAL IMAGE ===
        canvas.save(final_thumb, quality=95)
        
        # Cleanup
        if os.path.exists(temp_thumb):
            os.remove(temp_thumb)
        
        return final_thumb
        
    except Exception as e:
        print(f"Error creating custom thumbnail: {e}")
        import traceback
        traceback.print_exc()
        if os.path.exists(temp_thumb):
            try:
                os.remove(temp_thumb)
            except:
                pass
        return thumbnail_url


def draw_fallback_player(draw, canvas_width, font, controls_y_base, panel_width):
    """Draw basic player controls if image not found"""
    controls_y = controls_y_base # Use passed-in Y position
    
    # Dark control panel background
    # panel_width = 380 # CHANGED: Passed as argument
    panel_height = 75
    panel_x = (canvas_width - panel_width) // 2
    
    # Create a transparent RGBA version for the panel
    panel_img = Image.new("RGBA", (canvas_width, canvas_height), (0,0,0,0))
    panel_draw = ImageDraw.Draw(panel_img)
    
    # Draw the rounded rectangle with 75% opacity (alpha=190)
    panel_draw.rounded_rectangle(
        [panel_x, controls_y, panel_x + panel_width, controls_y + panel_height],
        radius=38,
        fill=(25, 25, 25, 190) # Added alpha for semi-transparency
    )
    
    # Button positions (5 buttons)
    center_x = canvas_width // 2
    btn_y = controls_y + 37
    
    # CHANGED: Adjusted offsets for smaller 380px width
    buttons = [
        (-130, "âŸ²", False),
        (-65, "â®", False),
        (0, "â¸", True),
        (65, "â­", False),
        (130, "âš¯", False)
    ]
    
    for x_offset, icon, is_center in buttons:
        btn_x = center_x + x_offset
        
        if is_center:
            radius = 24
            panel_draw.ellipse(
                [btn_x - radius, btn_y - radius, btn_x + radius, btn_y + radius],
                outline=(255, 255, 255, 190), # Added alpha
                width=3
            )
            panel_draw.text((btn_x, btn_y), icon, fill=(255, 255, 255, 190), font=font, anchor="mm") # Added alpha
        else:
            radius = 20
            panel_draw.ellipse(
                [btn_x - radius, btn_y - radius, btn_x + radius, btn_y + radius],
                outline=(180, 180, 180, 190), # Added alpha
                width=2
            )
            panel_draw.text((btn_x, btn_y), icon, fill=(180, 180, 180, 190), font=font, anchor="mm") # Added alpha

    # Paste the semi-transparent panel onto the main canvas
    draw.bitmap((0, 0), panel_img) 


def clean_text(text):
    """Clean text from special characters"""
    text = re.sub(r'[^\w\s\-\.\,\!\?\'\"]', '', text)
    return text


def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        try:
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
        except:
            width = len(test_line) * (font.size // 2)
            
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


async def cleanup_temp_thumbs():
    """Remove thumbnails older than 1 hour"""
    import time
    temp_dir = os.path.join("TNC_MUSIC", "temp")
    
    if os.path.isdir(temp_dir):
        current_time = time.time()
        for filename in os.listdir(temp_dir):
            if filename.startswith(("final_", "thumb_")):
                filepath = os.path.join(temp_dir, filename)
                try:
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > 3600:  # 1 hour
                        os.remove(filepath)
                except Exception as e:
                    print(f"Cleanup error: {e}")
                    pass