import streamlit as st


def card(text='', value='', symbol='', icon='', background=(255, 204, 0), fontsize=20):
    wch_colour_box = background
    wch_colour_font = (0, 0, 0)
    fontsize = fontsize
    valign = "left"
    iconname = icon
    sline = text
    lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
    if type(value) in (int, float):
        i = f'{value:,}'.replace(',', ' ') + ' ' + symbol
    else:
        i = str(value) + ' ' + symbol

    htmlstr = f"""<p style='background-color: rgb({wch_colour_box[0]}, 
                                                  {wch_colour_box[1]}, 
                                                  {wch_colour_box[2]}, 1); 
                            color: rgb({wch_colour_font[0]}, 
                                       {wch_colour_font[1]}, 
                                       {wch_colour_font[2]}, 0.85); 
                            font-size: {fontsize}px; 
                            border-radius: 7px; 
                            padding-left: 8px; 
                            padding-top: 18px; 
                            padding-bottom: 18px; 
                            line-height:25px;'>
                            <i class='{iconname} fa-s'></i> {sline}
                            </style><BR><span style='font-size: 18px; 
                            margin-top: 0;'>{i}</style></span></p>"""

    return st.markdown(lnk + htmlstr, unsafe_allow_html=True)
