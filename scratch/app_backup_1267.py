Created At: 2026-06-08T17:43:16Z
Completed At: 2026-06-08T17:43:16Z
File Path: `file:///c:/Users/menda/OneDrive/Desktop/AcademicAnalyser/app.py`
Total Lines: 998
Total Bytes: 38356
Showing lines 850 to 998
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
850:         if st.button("Logout", type="secondary"):
851:             logout_user()
852:             st.rerun()
853: 
854: 
855: def render_js_session_manager():
856:     """Render a hidden HTML block with an onerror script to manage localStorage session token synchronization."""
857:     # Check if we just logged out or have invalid session
858:     if st.session_state.get("logged_out", False) or st.session_state.get("clear_local_storage", False):
859:         js_code = (
860:             "try {"
861:             "localStorage.removeItem('session_token');"
862:             "localStorage.removeItem('page');"
863:             "localStorage.removeItem('history_view_id');"
864:             "window.location.search = '';"
865:             "} catch(e) { console.error(e); }"
866:         )
867:         st.markdown(f'<img src="x" onerror="{js_code}" style="display:none;"/>', unsafe_allow_html=True)
868:         st.session_state.logged_out = False
869:         st.session_state.clear_local_storage = False
870:         st.stop()
871: 
872:     # Get query params
873:     session_token = None
874:     page = st.session_state.page
875:     history_view_id = st.session_state.get("history_view_id")
876: 
877:     if hasattr(st, "query_params"):
878:         session_token = st.query_params.get("session_token")
879:     else:
880:         session_token = st.experimental_get_query_params().get("session_token", [None])[0]
881: 
882:     if session_token:
883:         # We have a token in URL. Save it to localStorage.
884:         history_id_str = f"'{history_view_id}'" if history_view_id el
<truncated 2893 bytes>
53:                     if stored_view_id != active_view_id:
954:                         st.query_params["history_view_id"] = active_view_id
955:                 else:
956:                     if "history_view_id" in st.query_params:
957:                         st.query_params.pop("history_view_id", None)
958:             else:
959:                 q_params = st.experimental_get_query_params()
960:                 stored_page = q_params.get("page", [None])[0]
961:                 stored_view_id = q_params.get("history_view_id", [None])[0]
962:                 active_view_id = st.session_state.get("history_view_id")
963:                 
964:                 needs_update = False
965:                 params = {"session_token": session_token}
966:                 
967:                 if stored_page != page:
968:                     needs_update = True
969:                 params["page"] = page
970:                 
971:                 if active_view_id:
972:                     params["history_view_id"] = active_view_id
973:                     if stored_view_id != active_view_id:
974:                         needs_update = True
975:                 else:
976:                     if stored_view_id is not None:
977:                         needs_update = True
978:                         
979:                 if needs_update:
980:                     st.experimental_set_query_params(**params)
981:                 
982:     if page == 'upload':
983:         upload_page()
984:     elif page == 'study':
985:         study_page()
986:     elif page == 'quiz_setup':
987:         quiz_setup_page()
988:     elif page == 'quiz':
989:         quiz_page()
990:     elif page == 'results':
991:         results_page()
992:     elif page == 'history':
993:         history_page()
994: 
995: 
996: if __name__ == "__main__":
997:     main()
998: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.
