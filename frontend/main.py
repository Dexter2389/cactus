import streamlit as st
import asyncio
import logging
import aiofiles
from pathlib import Path
from streamlit_player import st_player
from st_social_media_links import SocialMediaIcons
import aiohttp
import os

BASE_BACKEND_URL = os.getenv("BASE_BACKEND_URL", "http://localhost:8003")

# https://www.youtube.com/watch?v=VxMOx9ervF0


async def generate_reel(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_BACKEND_URL}/generate", json={"url": url}
        ) as response:
            if response.status == 200:
                try:
                    result = await response.json()
                    return result
                except Exception as e:
                    print(e)
            else:
                print(response.status)


async def main():
    st.set_page_config(
        layout="wide",
        page_title="Cactus - Short-form video generator",
    )

    social_media_links = [
        "https://www.facebook.com/cactus_facebook",
        "https://www.youtube.com/cactus_youtube",
        "https://www.instagram.com/cactus_instagram",
        "https://www.tiktok.com/cactus_tiktok",
    ]

    app_header = st.container()
    result_handler = st.container()

    with app_header:
        st.title("🌵 Cactus")
        st.markdown("##### 🎞️ Short-form content development platform")
        st.warning(
            "🚧️ This app is still in beta. Please [report any bugs] to the GitHub repo."
        )

    with st.sidebar:
        st.markdown(
            "## How to use\n"
            "1. 📺 Upload long-form Youtube Video\n"
            "2. 🚀 Run Generation\n"
            "---"
        )

        with st.form(key="my_form"):
            youtube_link = st.text_input(
                label="🔗 YouTube Link",
                placeholder="Enter your YouTube link",
                help="Enter your YouTube link of which you want resources to increase engagement.",
            )
            submit_button = st.form_submit_button(
                label="🚀 Run Generation", use_container_width=True
            )

            if submit_button:
                with st.spinner(
                    "🏗️ Building a Highlight reel... (this might take a while)"
                ):
                    api_response = await generate_reel(url=youtube_link)

                    if api_response:
                        with result_handler:
                            st_player(
                                url=f"{BASE_BACKEND_URL}/stream_file/{api_response.get('reel_file_id')}",
                                height=500,
                            )
                            generate_response_dict = api_response.get(
                                "generate_response"
                            )
                            st.markdown(f"### {generate_response_dict.get('title')}")
                            itinerary_list = generate_response_dict.get("itinerary")
                            for itinerary in itinerary_list:
                                st.markdown(f"#### {itinerary.get('segment')}")
                                st.markdown(
                                    f"**Description:** {itinerary.get('description')}"
                                )

                            with st.form(key="share_form"):
                                social_media_icons = SocialMediaIcons(
                                    social_media_links
                                )
                                social_media_icons.render(sidebar=False)
                                st.markdown("")
                                share_button = st.form_submit_button(
                                    label="🎉 Share your Highlight Reel 😉",
                                    use_container_width=True,
                                    disabled=True,
                                )


if __name__ == "__main__":
    asyncio.run(main())
