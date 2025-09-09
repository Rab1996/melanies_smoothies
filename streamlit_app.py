# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(f"Customize Your Smoothie! :cup_with_straw: {st.__version__}")
st.write("""Choose the fruits you want in your custom Smoothie!""")

# Input for name on order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)

# Convert Snowpark DataFrame to Pandas
pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# If ingredients are selected
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")
        SmoothieFroot_response = requests.get(
            "https://my.SMOOTHIEFROOT.com/api/fruit/{search_on}"
        )
        st.dataframe(data=SmoothieFroot_response.json(), use_container_width=True)

    # Prepare SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    # Submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
