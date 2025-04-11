# === app.py ===
# Versi Akhir (v1) dengan Penjanaan Prompt BM, EN, dan JSON Lengkap

import streamlit as st
import json
import os

# Tetapan halaman mesti jadi arahan Streamlit PERTAMA selepas import
st.set_page_config(page_title="Jana Prompt Komik", layout="wide")

# --- Definisi Fungsi ---
DATA_FILE = "characters.json"

def load_data(file_path):
    """Memuat data watak dari fail JSON. Menggunakan data default jika tiada fail/rosak/kosong."""
    default_data = {
        "Pak Leman": { "umur": 68, "fizikal": "Tinggi: 1.69 meter. Rambut warna beruban. Tidak bermisai atau berjanggut.", "pakaian": "Kemeja warna tiffany, seluar hitam, pakai capal, berkopiah putih.", "personaliti": "", "prompt_penuh": "" },
        "Pak Mail": { "umur": 65, "fizikal": "Tinggi: 1.58 meter. Rambut warna putih. Tidak bermisai atau berjanggut. Berkacamata.", "pakaian": "Kemeja warna pink, seluar hitam, pakai capal, bersongkok hitam.", "personaliti": "", "prompt_penuh": "" }
    }
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content:
                    st.info(f"Fail data '{file_path}' kosong. Memuatkan data default.")
                    return default_data
                data = json.loads(content)
                if not isinstance(data, dict):
                     st.warning(f"Format data dalam '{file_path}' tidak sah. Memuatkan data default.")
                     return default_data
                data_updated = False
                for char, details in default_data.items():
                    if char not in data:
                        data[char] = details
                        st.info(f"Watak '{char}' tiada dalam fail data, dimuatkan dari default.")
                        data_updated = True
                    else:
                        # Pastikan semua kunci dari default ada dalam data dimuat
                        for key, default_value in details.items():
                            if key not in data[char]:
                                data[char][key] = default_value
                                data_updated = True # Tandakan jika ada penambahan
                # Jika data dikemas kini dengan kunci default, beri pilihan untuk simpan? Buat masa ini tidak.
                # if data_updated: st.info("Struktur data dikemas kini dengan medan default.")
                return data
        except json.JSONDecodeError:
            st.error(f"Ralat membaca fail {file_path}. Fail mungkin rosak. Memuatkan data default.")
            return default_data
        except Exception as e:
            st.error(f"Ralat tidak dijangka semasa memuat fail {file_path}: {e}. Memuatkan data default.")
            return default_data
    else:
        st.info(f"Fail '{DATA_FILE}' tidak ditemui. Memuatkan data default. Fail baru akan dicipta apabila data disimpan.")
        return default_data

def save_data(file_path, data):
    """Menyimpan data watak ke fail JSON."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}") # Log ralat ke terminal
        return False

def generate_prompt_bm(input_data, character_db):
    """Menjana prompt deskriptif dalam Bahasa Melayu."""
    prompt_parts = []
    prompt_parts.append(f"Sebuah panel komik dalam [{input_data['visual_style']}].")
    if input_data['background']: prompt_parts.append(f"Berlatarbelakangkan: {input_data['background']}.")
    else: prompt_parts.append("Latar belakang tidak dinyatakan secara spesifik.")
    if input_data['selected_characters']:
        char_descriptions = []
        for char_name in input_data['selected_characters']:
            details = character_db.get(char_name, {}); desc = f"[{char_name}"
            details_list = []
            if details.get('fizikal'): details_list.append(details['fizikal'])
            if details.get('pakaian'): details_list.append(f"memakai {details['pakaian']}")
            if details.get('personaliti'): details_list.append(f"bersifat {details['personaliti']}")
            if details_list: desc += f" ({', '.join(details_list)})"
            desc += "]"
            char_descriptions.append(desc)
        prompt_parts.append(f"Memaparkan watak: {', '.join(char_descriptions)}.")
        if len(input_data['selected_characters']) > 1: prompt_parts.append(f"Watak-watak tersebut sedang berinteraksi antara satu sama lain.")
        elif len(input_data['selected_characters']) == 1: prompt_parts.append(f"{input_data['selected_characters'][0]} sedang melakukan sesuatu (aksi tidak dinyatakan).")
    else: prompt_parts.append("Tiada watak spesifik dalam panel ini.")
    if input_data['dialogues']:
        dialogue_summary = [f"{char_name} berkata \"{text}\"" for char_name, text in input_data['dialogues'].items()]
        prompt_parts.append("Dialog yang kedengaran: " + "; ".join(dialogue_summary) + ".")
    if input_data['extra_text']: prompt_parts.append(f"Teks tambahan seperti kapsyen atau bunyi: \"{input_data['extra_text']}\".")
    if input_data['comic_title']: prompt_parts.append(f"(Konteks dari komik: '{input_data['comic_title']}')")
    return " ".join(prompt_parts)

def generate_prompt_en(input_data, character_db):
    """Generates a descriptive prompt in English."""
    prompt_parts = []
    prompt_parts.append(f"A comic panel in the style of [{input_data['visual_style']}].")
    if input_data['background']: prompt_parts.append(f"Background: {input_data['background']}.")
    else: prompt_parts.append("The background is not specifically described.")
    if input_data['selected_characters']:
        char_descriptions = []
        for char_name in input_data['selected_characters']:
            details = character_db.get(char_name, {}); desc = f"[{char_name}"
            details_list = []
            if details.get('umur'): details_list.append(f"around {details['umur']} years old")
            if details.get('fizikal'): details_list.append(details['fizikal'])
            if details.get('pakaian'): details_list.append(f"wearing {details['pakaian']}")
            if details.get('personaliti'): details_list.append(f"with personality traits: {details['personaliti']}")
            if details_list: desc += f" ({', '.join(details_list)})"
            desc += "]"
            char_descriptions.append(desc)
        prompt_parts.append(f"Featuring characters: {', '.join(char_descriptions)}.")
        if len(input_data['selected_characters']) > 1: prompt_parts.append(f"The characters are interacting with each other.")
        elif len(input_data['selected_characters']) == 1: prompt_parts.append(f"{input_data['selected_characters'][0]} is present in the scene, action unspecified.")
    else: prompt_parts.append("No specific characters are featured in this panel.")
    if input_data['dialogues']:
        dialogue_summary = [f"{char_name} says: \"{text}\"" for char_name, text in input_data['dialogues'].items()]
        prompt_parts.append("Dialogue includes: " + "; ".join(dialogue_summary) + ".")
    if input_data['extra_text']: prompt_parts.append(f"Additional text (caption/sound): \"{input_data['extra_text']}\".")
    if input_data['comic_title']: prompt_parts.append(f"(Context from the comic titled: '{input_data['comic_title']}')")
    return " ".join(prompt_parts)

# === Mulakan Aplikasi Streamlit ===

if 'character_data' not in st.session_state:
    st.session_state.character_data = load_data(DATA_FILE)

st.title("Aplikasi Jana Prompt Komik")

tab1, tab2 = st.tabs(["Penjana Prompt Komik", "Pengurus Data Watak"])

# === TAB 1: Penjana Prompt Komik ===
with tab1:
    st.header("Penjana Prompt Komik (Per Bingkai)")
    st.write("Masukkan butiran untuk menjana prompt bagi satu bingkai komik.")

    comic_title = st.text_input("Judul Komik (Keseluruhan):", key="comic_title", value=st.session_state.get('comic_title_val', ''))
    if comic_title != st.session_state.get('comic_title_val', ''): st.session_state.comic_title_val = comic_title

    style_options = [
        "Gaya LAT (Kartun Malaysia)", "Gaya Studio Ghibli", "Gaya Suasana Kampung",
        "Gaya Watercolor (Cat Air)", "Gaya Warna Pastel", "Gaya Manga Jepun (Hitam Putih)",
        "Gaya Komik Amerika (Warna Terang)", "Gaya Kartun Comel (Chibi)", "Gaya Realistik"
    ]
    selected_style = st.selectbox("Pilih Gaya Visual Komik:", options=style_options, key="comic_style")

    st.divider()

    with st.container(border=True):
        st.subheader("Butiran Bingkai 1")
        character_list = list(st.session_state.character_data.keys())
        selected_chars_frame1 = st.multiselect("Watak dalam Bingkai Ini:", options=character_list, key="frame1_chars")
        bg_desc_frame1 = st.text_area("Latar Belakang Bingkai:", key="frame1_bg", height=100)
        with st.expander("Dialog Watak (Isi jika perlu)"):
            dialogues_frame1 = {}
            if selected_chars_frame1:
                for char in selected_chars_frame1: dialogues_frame1[char] = st.text_input(f"Dialog {char}:", key=f"frame1_dialog_{char}")
            else: st.info("Pilih sekurang-kurangnya satu watak di atas untuk memasukkan dialog.")
        extra_text_frame1 = st.text_input("Teks Tambahan (Kapsyen/Bunyi):", key="frame1_extra")

    # --- Butang dan Logik Penjanaan ---
    # Tempat untuk paparkan output
    output_placeholder = st.container()

    if st.button("Jana Prompt untuk Bingkai Ini", key="btn_generate"):
        # Kumpul input
        frame_input_data = {
            "comic_title": comic_title, "visual_style": selected_style, "frame_number": 1,
            "selected_characters": selected_chars_frame1, "background": bg_desc_frame1,
            "dialogues": {char: text for char, text in dialogues_frame1.items() if text}, # Hanya ambil dialog yang diisi
            "extra_text": extra_text_frame1
        }

        # Panggil Fungsi Penjanaan
        prompt_bm_result = generate_prompt_bm(frame_input_data, st.session_state.character_data)
        prompt_en_result = generate_prompt_en(frame_input_data, st.session_state.character_data)

        # === Logik Penjanaan JSON (Dikemaskini) ===
        try:
            # Mulakan dengan data input bingkai
            json_output_data = frame_input_data.copy()

            # Tambah prompt yang dijana
            json_output_data["generated_prompt_bm"] = prompt_bm_result
            json_output_data["generated_prompt_en"] = prompt_en_result

            # (Pilihan) Tambah butiran watak yang digunakan dalam bingkai ini
            selected_char_details = {}
            for char_name in frame_input_data["selected_characters"]:
                # Ambil butiran dari session_state, tapi kecualikan 'prompt_penuh' jika tak relevan
                details_to_include = {k: v for k, v in st.session_state.character_data.get(char_name, {}).items() if k != 'prompt_penuh'}
                selected_char_details[char_name] = details_to_include
            json_output_data["character_details_used"] = selected_char_details

            # Tukar ke string JSON yang diformat
            json_output_string = json.dumps(json_output_data, indent=4, ensure_ascii=False)

        except Exception as e:
            # Tangani ralat jika proses JSON gagal
            json_output_string = f'{{"error": "Gagal menjana output JSON.", "detail": "{str(e)}"}}'
            st.error(f"Ralat semasa menjana JSON: {e}")
        # ================================

        # Paparkan Hasil Penjanaan dalam placeholder
        with output_placeholder:
            st.success("Prompt berjaya dijana!")
            st.write("Data Input Bingkai (Untuk Rujukan):") # Papar semula input
            st.json(frame_input_data) # Guna st.json untuk paparan input yang lebih kemas
            st.divider()
            st.subheader("Hasil Prompt:")
            col_bm, col_en, col_json_out = st.columns(3) # Susun output dalam 3 lajur
            with col_bm:
                st.text_area("Prompt Bahasa Melayu", value=prompt_bm_result, height=350, key="output_bm_f1_final")
            with col_en:
                st.text_area("Prompt Bahasa Inggeris", value=prompt_en_result, height=350, key="output_en_f1_final")
            with col_json_out: # Guna nama pembolehubah berbeza untuk elak konflik
                st.markdown("**Output JSON:**") # Tambah tajuk untuk JSON
                st.code(json_output_string, language="json", line_numbers=True) # Papar JSON


# === TAB 2: Pengurus Data Watak ===
with tab2:
    # ... (Kod untuk Tab 2 kekal SAMA seperti versi sebelumnya) ...
    st.header("Pengurus Data Watak")
    st.write("Tambah, edit, atau lihat butiran watak yang disimpan.")
    with st.form(key="character_form_tab2", clear_on_submit=False):
        available_characters_tab2 = list(st.session_state.character_data.keys())
        character_options_tab2 = ["Tambah Watak Baru..."] + available_characters_tab2
        selected_char_name_option_tab2 = st.selectbox("Pilih Watak atau Tambah Baru:", options=character_options_tab2, key="sb_select_char_tab2")
        new_char_name_tab2 = ""
        if selected_char_name_option_tab2 == "Tambah Watak Baru...":
            new_char_name_tab2 = st.text_input("Nama Watak Baru:", key="ti_new_char_name_tab2")
            char_to_edit_tab2 = new_char_name_tab2.strip(); current_details_tab2 = st.session_state.character_data.get(char_to_edit_tab2, {}) if char_to_edit_tab2 in st.session_state.character_data else {}
            if char_to_edit_tab2 in st.session_state.character_data: st.info(f"Mengedit watak sedia ada: '{char_to_edit_tab2}'")
        else: char_to_edit_tab2 = selected_char_name_option_tab2; current_details_tab2 = st.session_state.character_data.get(char_to_edit_tab2, {})
        if char_to_edit_tab2:
            st.write(f"**Memasukkan/Mengedit Butiran untuk: {char_to_edit_tab2}**")
            age_tab2 = st.number_input("Anggaran Umur:", min_value=0, max_value=150, value=current_details_tab2.get("umur", 0), key=f"num_{char_to_edit_tab2}_age_tab2")
            physical_desc_tab2 = st.text_area("Deskripsi Fizikal:", value=current_details_tab2.get("fizikal", ""), height=100, placeholder="Contoh: Tinggi, kurus...", key=f"ta_{char_to_edit_tab2}_fizikal_tab2")
            clothing_tab2 = st.text_input("Pakaian Biasa:", value=current_details_tab2.get("pakaian", ""), placeholder="Contoh: Baju Melayu...", key=f"ti_{char_to_edit_tab2}_pakaian_tab2")
            personality_tab2 = st.text_area("Personaliti/Sifat:", value=current_details_tab2.get("personaliti", ""), height=100, placeholder="Contoh: Garang tapi baik hati...", key=f"ta_{char_to_edit_tab2}_personaliti_tab2")
            full_prompt_tab2 = st.text_area("Prompt Penuh (untuk AI):", value=current_details_tab2.get("prompt_penuh", ""), height=150, placeholder="[Akan dijana kemudian atau isi manual jika perlu]", key=f"ta_{char_to_edit_tab2}_prompt_tab2")
        else:
            if selected_char_name_option_tab2 == "Tambah Watak Baru...": st.info("Sila masukkan nama untuk watak baru.")
        submitted_tab2 = st.form_submit_button("Simpan Perincian Watak");
        if submitted_tab2:
            final_char_name_tab2 = char_to_edit_tab2
            if not final_char_name_tab2: st.warning("Sila pilih watak atau masukkan nama watak baru sebelum menyimpan.")
            else:
                new_details_tab2 = { "umur": age_tab2, "fizikal": physical_desc_tab2, "pakaian": clothing_tab2, "personaliti": personality_tab2, "prompt_penuh": full_prompt_tab2 }
                st.session_state.character_data[final_char_name_tab2] = new_details_tab2
                if save_data(DATA_FILE, st.session_state.character_data): st.success(f"Perincian untuk '{final_char_name_tab2}' telah berjaya disimpan ke {DATA_FILE}!")
                else: st.error(f"Gagal menyimpan data ke {DATA_FILE}.")
    st.divider()
    st.header("Lihat Perincian Watak Tersimpan"); display_options_tab2 = list(st.session_state.character_data.keys())
    if not display_options_tab2: st.info("Tiada data watak tersimpan untuk dipaparkan.")
    else:
        char_to_display_tab2 = st.selectbox("Pilih Watak untuk Lihat Perincian:", options=display_options_tab2, key="sb_display_char_tab2")
        if char_to_display_tab2 and char_to_display_tab2 in st.session_state.character_data:
            details_to_display_tab2 = st.session_state.character_data[char_to_display_tab2]
            st.subheader(f"Perincian untuk {char_to_display_tab2}")
            st.write(f"**Umur:** {details_to_display_tab2.get('umur', 'Tiada data')}"); st.write(f"**Fizikal:** {details_to_display_tab2.get('fizikal', 'Tiada data')}")
            st.write(f"**Pakaian:** {details_to_display_tab2.get('pakaian', 'Tiada data')}"); st.write(f"**Personaliti:** {details_to_display_tab2.get('personaliti', 'Tiada data')}")
            st.text_area("Prompt Penuh Tersimpan:", value=details_to_display_tab2.get('prompt_penuh', '[Tiada data atau akan dijana]'), height=150, disabled=True, key=f"disp_ta_{char_to_display_tab2}_prompt_tab2")
    st.divider()
    st.header("Pengurusan Fail Data"); st.subheader("Simpan Sebagai (Save As)")
    save_as_filename_tab2 = st.text_input("Nama Fail Baru (.json):", value="characters_copy.json", key="ti_save_as_name_tab2")
    if st.button("Simpan Data ke Fail Baru", key="btn_save_as_tab2"):
        save_as_filename_tab2 = save_as_filename_tab2.strip();
        if save_as_filename_tab2:
            if not save_as_filename_tab2.lower().endswith('.json'): save_as_filename_tab2 += '.json'
            if save_as_filename_tab2 == DATA_FILE: st.warning(f"'{DATA_FILE}' adalah fail utama. Sila guna nama lain.")
            else:
                if save_data(save_as_filename_tab2, st.session_state.character_data): st.success(f"Data berjaya disimpan sebagai '{save_as_filename_tab2}'!")
                else: st.error(f"Gagal menyimpan data sebagai '{save_as_filename_tab2}'.")
        else: st.warning("Sila masukkan nama fail untuk 'Save As'.")
    st.subheader("Muat Turun Data");
    try:
        data_to_download_tab2 = st.session_state.character_data; json_string_tab2 = json.dumps(data_to_download_tab2, indent=4, ensure_ascii=False)
        st.download_button(label="Muat Turun Fail Data (JSON)", data=json_string_tab2.encode('utf-8'), file_name="characters_export.json", mime="application/json", key="btn_download_tab2")
    except Exception as e: st.error(f"Gagal menyediakan data untuk muat turun: {e}")
    st.divider(); st.caption(f"Data utama dimuat/disimpan dari {DATA_FILE}")

# === Tamat app.py ===
