Created At: 2026-06-08T17:38:10Z
Completed At: 2026-06-08T17:38:10Z
File Path: `file:///c:/Users/menda/OneDrive/Desktop/AcademicAnalyser/app.py`
Total Lines: 1074
Total Bytes: 41090
Showing lines 885 to 1074
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
885:                 if st.session_state.quiz_submitted:
886:                     answered = sum(1 for ans in st.session_state.user_answers if ans is not None)
887:                     st.metric("Answered", f"{answered}/{len(st.session_state.quiz_questions)}")
888:             st.markdown("---")
889:         
890:         st.markdown("### 🔑 API Status")
891:         if st.session_state.api_key:
892:             st.success(f"✅ Connected")
893:         else:
894:             st.error("❌ Not Connected")
895:             
896:         st.markdown("---")
897:         if st.button("Logout", type="secondary"):
898:             logout_user()
899:             st.rerun()
900: 
901: 
902: def render_js_session_manager():
903:     """Render a hidden HTML/JS block in an iframe to manage localStorage session token synchronization."""
904:     import streamlit.components.v1 as components
905: 
906:     # Check if we just logged out or have invalid session
907:     if st.session_state.get("logged_out", False) or st.session_state.get("clear_local_storage", False):
908:         components.html(
909:             """
910:             <script>
911:                 try {
912:                     window.parent.localStorage.removeItem("session_token");
913:                     window.parent.localStorage.removeItem("page");
914:                     window.parent.localStorage.removeItem("history_view_id");
915:                     window.parent.location.search = "";
916:                 } catch (e) {
917:                     console.error("Session clear error:", e);
918:                 }
9
<truncated 4391 bytes>
active_view_id:
1030:                         st.query_params["history_view_id"] = active_view_id
1031:                 else:
1032:                     if "history_view_id" in st.query_params:
1033:                         st.query_params.pop("history_view_id", None)
1034:             else:
1035:                 q_params = st.experimental_get_query_params()
1036:                 stored_page = q_params.get("page", [None])[0]
1037:                 stored_view_id = q_params.get("history_view_id", [None])[0]
1038:                 active_view_id = st.session_state.get("history_view_id")
1039:                 
1040:                 needs_update = False
1041:                 params = {"session_token": session_token}
1042:                 
1043:                 if stored_page != page:
1044:                     needs_update = True
1045:                 params["page"] = page
1046:                 
1047:                 if active_view_id:
1048:                     params["history_view_id"] = active_view_id
1049:                     if stored_view_id != active_view_id:
1050:                         needs_update = True
1051:                 else:
1052:                     if stored_view_id is not None:
1053:                         needs_update = True
1054:                         
1055:                 if needs_update:
1056:                     st.experimental_set_query_params(**params)
1057:                 
1058:     if page == 'upload':
1059:         upload_page()
1060:     elif page == 'study':
1061:         study_page()
1062:     elif page == 'quiz_setup':
1063:         quiz_setup_page()
1064:     elif page == 'quiz':
1065:         quiz_page()
1066:     elif page == 'results':
1067:         results_page()
1068:     elif page == 'history':
1069:         history_page()
1070: 
1071: 
1072: if __name__ == "__main__":
1073:     main()
1074: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.
