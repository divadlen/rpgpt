import streamlit as st
from streamlit import session_state as state
import streamlit.components.v1 as components
import hydralit as hy

import os


st.set_page_config(
  page_title="RPGPT",
  page_icon='assets/n-mark-color.png',
  layout="wide",
  initial_sidebar_state="collapsed",
)

over_theme = {'txc_inactive': '#FFFFFF', 'txc_active':'#A9DEF9'}
navbar_theme = {'txc_inactive': '#FFFFFF','txc_active':'grey','menu_background':'white','option_active':'blue'}


#---Start app---#
def run_app():    
  state['user_level'] = state.get('user_level', 1)
  user_level = state.get("user_level", 1)
  state['ADMIN_MODE'] = state.get("ADMIN_MODE", False)
  state['ANTHROPIC_API_KEY'] = state.get("ANTHROPIC_API_KEY", None)

  #---Start Hydra instance---#
  hydra_theme = None # init hydra theme
  

  with st.sidebar:
    c1, c2 = st.columns([1, 1])
    with c1:
      if state['ADMIN_MODE'] == True:
        exit = st.button('Exit Admin')
        if exit:
          state['ADMIN_MODE'] = False
          state['ANTHROPIC_API_KEY'] = None
          st.experimental_fragment()

    with c2:
      if state['ANTHROPIC_API_KEY'] is not None:
        clear_api_key = st.button('Clear API Key')
        if clear_api_key:
          state['ANTHROPIC_API_KEY'] = None
          st.experimental_fragment()
        

    with st.form('Admin Login'):
      ADMIN_PW = st.text_input('Admin Password', value=None, type='password')
      submit_button = st.form_submit_button('Login')
      if ADMIN_PW == st.secrets['ADMIN_PW'] and submit_button:
        state['user_level'] = 2
        state['ANTHROPIC_API_KEY'] = st.secrets['ANTHROPIC_API_KEY']
        state['ADMIN_MODE'] = True
        st.experimental_fragment()

    with st.form('Enter API Key'):
      ANTHROPIC_API_KEY = st.text_input('Anthropic API Key', value=None, type='password')
      submit_button = st.form_submit_button('Submit')
      if ANTHROPIC_API_KEY and submit_button:
        state['ANTHROPIC_API_KEY'] = ANTHROPIC_API_KEY
        st.experimental_fragment()

    with st.expander('About'):
      st.info('Bru')
      st.write('Version: 0.0.1')

      st.write(""":large_blue_square: [Twitter](https://twitter.com/just_neldivad)""")
      st.markdown(""":notebook: [GitHub](https://github.com/neldivad)""")
      




  app = hy.HydraApp(
    hide_streamlit_markers=False,
    use_navbar=True, 
    navbar_sticky=False,
    navbar_animation=True,
    navbar_theme=over_theme,
  )

  #specify a custom loading app for a custom transition between apps, this includes a nice custom spinner
  from apps._loading import MyLoadingApp
  app.add_loader_app(MyLoadingApp(delay=0))

  #---Add apps from folder---#
  @app.addapp(is_home=True, title='Home')
  def homeApp():
    from apps.home import main
    main()

  @app.addapp(title='Get Questions')
  def get_questions():
    from apps.question_get import main
    main()

  @app.addapp(title='Read Question')
  def read_question():
    from apps.question_read import main
    main()

  @app.addapp(title='Review Answer')
  def review_answer():
    from apps.answer_review import main
    main()

  @app.addapp(title='AI Chat')
  def ai_chat():
    from apps.ai_chat import main
    main()

  @app.addapp(title='Logout')
  def logoutApp():
    from apps.logout import main
    main()


  #--- Level 1 apps ---#
  if user_level < 2: 
    pass

  #--- Level 2 apps ---#
  if user_level >= 2:
    pass



  def build_navigation(user_level=1):
    complex_nav = {}
    
    # Always add Home first
    complex_nav["Home"] = ['Home']

    # Other apps
    complex_nav["Get Questions"] = ['Get Questions']
    complex_nav["Read Question"] = ['Read Question']
    complex_nav["Review Answer"] = ['Review Answer']
    complex_nav["AI Chat"] = ['AI Chat']

    complex_nav["logout"] = ['Logout'] # key must be 'logout' idk why 
    return complex_nav
  

  complex_nav = build_navigation(user_level)
  app.run(complex_nav=complex_nav)



    


if __name__ == '__main__':
  run_app()