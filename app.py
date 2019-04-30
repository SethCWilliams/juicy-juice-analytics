from flask import Flask, render_template
import requests
from flask_humanize import Humanize

# try:
#     from juicykey import app_id, app_key
# except:
app_id = process.env.key_one
app_key = process.env.key_two

app = Flask(__name__)
humanize = Humanize(app)

@app.route("/")
def index():
    result_span = []
    unique_ingredient_list = []
    unique_ingredient_index = {}
    total_of_each_items_cal_per_oz = 0
    lower_search_result = 0
    higher_search_result = 50
    total_hits = 1
    while len(result_span) != total_hits:
            nutrionix_data = requests.get("https://api.nutritionix.com/v1_1/search/?brand_id=51db37d0176fe9790a899db2&results={}:{}&fields=*&appId={}&appKey={}".format(lower_search_result, higher_search_result, app_id, app_key))
            nutrionix_data_json = nutrionix_data.json()
            nutrionix_hits = nutrionix_data_json['hits']

            lower_search_result += 50
            higher_search_result += 50
            total_hits = nutrionix_data_json['total_hits']

            for item in nutrionix_hits:
                fields = item['fields']
                result_span.append(fields)

    for result in result_span:
        if result['nf_ingredient_statement'] is None:
            pass
        else:

            first_del_pos = result['nf_ingredient_statement'].find("(")  # get the position of [
            second_del_pos = result['nf_ingredient_statement'].find("),")  # get the position of ]
            string_after_replace = result['nf_ingredient_statement'].replace(result['nf_ingredient_statement']
                                                                         [first_del_pos - 1:second_del_pos + 1], "").replace(".", "").title().replace("And ", "")

            ingredient_list = string_after_replace.split(", ")

            for ingredient in ingredient_list:
                if ingredient not in unique_ingredient_list:
                    print("ingredient, dude", ingredient)
                    unique_ingredient_list.append(ingredient)
                    unique_ingredient_index.setdefault(ingredient, []).append(result['item_name'])
                else:
                    unique_ingredient_index.setdefault(ingredient, []).append(result['item_name'])

        if result['nf_serving_size_unit'] == "fl oz":
            divided_up = result['nf_calories'] / 8
            total_of_each_items_cal_per_oz += divided_up
        elif result['nf_serving_size_unit'] == 'box':
            # assuming that all pouches are the 4.23 oz packages due to them being in packages of 8
            divided_up = result['nf_calories'] / 4.23
            total_of_each_items_cal_per_oz += divided_up
        elif result['nf_serving_size_unit'] == 'bottle':
            # Assuming that the bottle is for the 10 oz packages only because on the juicy juice nutrition facts,
            #it starts going by fl oz on the 48 oz bottles. https://juicyjuice.com/products/juicy-juice-fruit-juice/apple
            divided_up = result['nf_calories'] / 10
            total_of_each_items_cal_per_oz += divided_up
        else:
            # assuming that all pouches are 6 oz
            divided_up = result['nf_calories'] / 6
            total_of_each_items_cal_per_oz += divided_up

    ctx = {
        'total': nutrionix_data_json['total_hits'],
        'fields': result_span,
        'ingredients': unique_ingredient_list,
        'calories_per_oz': round(total_of_each_items_cal_per_oz / len(result_span)),
        'index': unique_ingredient_index
    }
    print("index", unique_ingredient_index)
    return render_template('index.html', **ctx)

    # ctx = {
    #     'index': {1: [1, 2, 3], 2: [1, 2, 3], 3: [2, 4, 5], 4: ['skdje', 'dfnkw'], 5: [5, 3, 2533], 6: [1, 2, 3], 7: [1, 2, 3], 8: [1, 2, 3], 9: [11, 22, 33, 44], 10: ['afs', 'fjknel', 'fasd;'], 11: ['fad', 'sad', 'dad']}
    # }
    # return render_template('index.html', **ctx)


if __name__ == '__main__':
    app.run()
