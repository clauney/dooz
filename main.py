'''
TODO
1. how does requirements.txt function across *subtrees*? (pretty sure: answer = manual)

'''

from flask import Flask, render_template#, flash, send_file, request, redirect, escape, make_response, session, url_for, Response, Blueprint
import sys

app = Flask(__name__)
from datetime import datetime
import configerator

#%% CONFIG, pull into separate thinger

localconfig = {
        'name': 'local_config',
        'type': 'local_config',
        'data': {
                'alltasks': [
                        ['1000','Riley','AMPM','Teeth','Brush, use waterpik, use brush thingies'],
                        ['1001','Riley','PM','Shower','Shower, making sure that you wash your hair at least every other day'],
                        ['1002','Riley','AM','Breakfast','eat something with protein!'],
                        ['2001','Chris','AM','Pill','Take your meds'],
                        ['2002','Chris','AM','Vitamins','Take your vitamins'],
                        ['2003','Chris','AMPM','Check calendar','Take a look at the coming day'],
                        ['2004','Chris','PM','Shower','Take a shower!'],
                        ['2005','Chris','PM','Shoulder exercises','Do your shoulder exercises!'],
                        ['2006','Chris','AMPM','Teeth','Brush and floss!'],
                        ['2007','Chris','PM','Set out clothes','Set out your clothes for tomorrow']
                        ],
                'weather_loc_meteo': {
                        '98117': 'seattle_united-states-of-america_5809844',
                        },
                'who_data': {
                        'default': {
                                'zip': '98117',
                                },
                        'chris': {
                                },
                        },
                'unused_weatherwidget': '''<a class="weatherwidget-io" href="https://forecast7.com/en/47d69n122d38/98117/?unit=us" data-label_1="BALLARD" data-label_2="WEATHER" data-theme="weather_one" >BALLARD WEATHER</a>
                        <script>
                        !function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src='https://weatherwidget.io/js/widget.min.js';fjs.parentNode.insertBefore(js,fjs);}}(document,'script','weatherwidget-io-js');
                        </script>''',
                'meteo': '''<iframe src="https://www.meteoblue.com/en/weather/widget/three/seattle_united-states-of-america_5809844"  frameborder="0" scrolling="NO" allowtransparency="true" sandbox="allow-same-origin allow-scripts" style="width: 460px;height: 525px"></iframe>''',
                'craptraffic': '''<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d172152.17919202129!2d-122.32018107603865!3d47.60906576366696!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2sus!4v1520124306339" width="600" height="450" frameborder="0" style="border:0" allowfullscreen></iframe>''',
        
                },
        }

cliconfig = {'name': 'cli_params', 'type': 'cli_params', 'sysargv': sys.argv}

cfg = configerator.Configerator(config_sources=[localconfig, cliconfig],
#                                store_cfgtypes_in_envvar=[str],
                                )
rc = cfg.running_config
print('run webapp?', rc.get('runwebapp'))

#meteo='''<iframe src="https://www.meteoblue.com/en/weather/widget/three/seattle_united-states-of-america_5809844?geoloc=fixed&nocurrent=0&nocurrent=1&noforecast=0&days=4&tempunit=FAHRENHEIT&windunit=MILE_PER_HOUR&layout=image"  frameborder="0" scrolling="NO" allowtransparency="true" sandbox="allow-same-origin allow-scripts allow-popups allow-popups-to-escape-sandbox" style="width: 460px;height: 506px"></iframe><div><!-- DO NOT REMOVE THIS LINK --><a href="https://www.meteoblue.com/en/weather/forecast/week/whitewater_united-states-of-america_4281710?utm_source=weather_widget&utm_medium=linkus&utm_content=three&utm_campaign=Weather%2BWidget" target="_blank">meteoblue</a></div>'''

#%%
class ClientManager():
    def __init__(self, client_configs, **kwargs):
        '''
        '''
        self.name = kwargs.get('name')
        # later parse client_configs into clients

class FakeNewsDooz():
    def get_todo_msg(self, who):
        listostuff = self.todonow(who.title(), self.daypart()[0])
        prettylist = ''
        for item in listostuff:
            prettylist = prettylist + '<br>' + item[3] + ': ' + item[4]
        return 'Hello, ' + who.title() + '!<br>Have you done this stuff this ' + self.daypart()[1] + '?<br>' + prettylist
    
    def todonow(self, person,ampm):
        personalizedtasks=[]
        for task in alltasks:
            if task[1].title()==person.title() and ampm in task[2]:
                personalizedtasks.append(task)
        return personalizedtasks
    
    def daypart(self):
        if datetime.now().hour < 12:
            return ('AM','morning')
        else:
            return ('PM','evening')


dz = FakeNewsDooz()

#%% FLASK

@app.route('/todo/<who>')
def todo(who):
    return '<HTML><br>'+dz.get_todo_msg(who.title())+'<br><br>'+meteo+'</HTML>'
#    return render_template('doo.html',
#                           page_title='DOOZER: Dooz for {}'.format(who.title()),
#                           hello_str=get_todo_msg(who.title())
#                           )

if rc.get('runwebapp', '').upper() == 'TRUE':
    if __name__ == '__main__':
        app.run(debug=True)

