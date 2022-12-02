# !pip install streamlit
import streamlit as st
import pandas as pd
import calendar
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go

st.subheader('Laadpaaldata') 
st.subheader('Laadpaaldata_YEEEEEEEEEEEEEEEEEEEEEEET') 
st.text("Om de date op te schonen en overzichtelijk te maken hebben we de volgende bewerkingen uitgevoerd:")
st.text("Allereerst hebben we alle NA-waardes verwijderd.")
st.text("Vervolgens hebben we alle datums omgezet naar datetime format.")
st.text("Toen hebben we gegekeken of de aangesloten uren volgens de Ended-Started time wel overeen kwamen,")
st.text("hierbij waren er 5 erg afwijkend, dus hebben we deze verwijderd.")
st.text("Hevige 'uitschieters' hebben we verwijderd om de meest voorkomende oplaadtijden te kunnen plotten voor een beter overzicht")
st.text("De gemiddelde en mediaan zijn berekend om te implementeren in de volgende figuren.")
st.text("")

laadpaaldata = pd.read_csv('laadpaaldata.csv')
print(laadpaaldata.isna().sum().sum()) # Geen NaN waardes te vinden in deze dataset

# De waarnemingen waarbij het opladen later begint dan eindigt verwijderen, dit is immers onmogelijk en wij hebben er geen goede verklaring voor
laadpaaldata = laadpaaldata[laadpaaldata['Ended']>=laadpaaldata['Started']]

# De tijden omzetten naar een datetime waarde
laadpaaldata['Started'] =  pd.to_datetime(laadpaaldata['Started'], format='%Y-%m-%d  %H:%M:%S', errors='coerce') # Day is out of range for month, dus errors='coerce'
laadpaaldata['Ended'] =  pd.to_datetime(laadpaaldata['Ended'], format='%Y-%m-%d  %H:%M:%S', errors='coerce') # Day is out of range for month, dus errors='coerce'
laadpaaldata['Maand'] = pd.DatetimeIndex(laadpaaldata['Started']).month

# Tijd berekenen dat de auto aangesloten staat aan de laadpaal en het verschil met de daadwerkelijke oplaadtijd
laadpaaldata['LaadsessieAangesloten'] = laadpaaldata['Ended'] - laadpaaldata['Started']
laadpaaldata['LaadsessieAangeslotenUren'] = laadpaaldata['LaadsessieAangesloten'].dt.components['days']*24 + laadpaaldata['LaadsessieAangesloten'].dt.components['hours'] + laadpaaldata['LaadsessieAangesloten'].dt.components['minutes']/60 + laadpaaldata['LaadsessieAangesloten'].dt.components['seconds']/(60*60)
laadpaaldata['ConnectedAangeslotenDif'] = laadpaaldata['ConnectedTime'] - laadpaaldata['LaadsessieAangeslotenUren']

# De 5 waardes waarbij het verschil in ChargeTime en AangeslotenTime daadwerkelijk meet dan 0,1 uur verschilt
laadpaaldata = laadpaaldata[((laadpaaldata['ConnectedAangeslotenDif'] < 0.1) & (laadpaaldata['ConnectedAangeslotenDif'] > 0)) | ((laadpaaldata['ConnectedAangeslotenDif'] > -0.1) & (laadpaaldata['ConnectedAangeslotenDif'] < 0))]

# Hele lange tijden van laadsessie, de aansluiting, eruit halen
q_laad = laadpaaldata['LaadsessieAangeslotenUren'].quantile(0.965)
laadpaaldata[laadpaaldata['LaadsessieAangeslotenUren']<q_laad]
q_low_laad = laadpaaldata['LaadsessieAangeslotenUren'].quantile(0.035)
q_hi_laad = laadpaaldata['LaadsessieAangeslotenUren'].quantile(0.965)
laadpaaldata = laadpaaldata[(laadpaaldata["LaadsessieAangeslotenUren"] < q_hi_laad) & (laadpaaldata["LaadsessieAangeslotenUren"] > q_low_laad)]

# Hele lange tijden van chargetime eruit halen
q_charge = laadpaaldata['ChargeTime'].quantile(0.965)
laadpaaldata[laadpaaldata['ChargeTime']<q_charge]
q_low_charge = laadpaaldata['ChargeTime'].quantile(0.35)
q_hi_charge = laadpaaldata['ChargeTime'].quantile(0.965)
laadpaaldata = laadpaaldata[(laadpaaldata["ChargeTime"] < q_hi_charge) & (laadpaaldata["ChargeTime"] > q_low_charge)]

print(laadpaaldata.head())
st.dataframe(laadpaaldata)

# Dubbel check of de uitschieters weg zijn
# fig = px.box(laadpaaldata, x="ChargeTime")
# fig.show()
# fig = px.box(laadpaaldata, x="LaadsessieAangeslotenUren")
# fig.show()

gemiddelde = round(laadpaaldata['ChargeTime'].mean(), 4)
mediaan = round(laadpaaldata['ChargeTime'].median(), 4)
print('Gemiddelde: ' +str(int(gemiddelde))+ " uur en " +str(round((gemiddelde-int(gemiddelde))*60)) +" minuten")
print('Mediaan: ' +str(int(mediaan))+ " uur en " +str(round((mediaan-int(mediaan))*60)) +" minuten")

st.text('In onderstaand figuur is de verdeling te zien van de tijd dat een auto oplaadt.')
st.text('Het gemiddelde en de mediaan verschillen weinig. Wel is er duidelijk te zien dat zich twee toppen vormen,')
st.text("een bimodale normale verdeling waarschijnlijk. De meeste auto's laden iets meer dan 2 uur op.")

fig = px.histogram(laadpaaldata, x="ChargeTime", nbins=40, text_auto=True,
            title='Aantal laadpalen per oplaadtijd',
            labels={"ChargeTime":"Oplaadtijd (in uren)"})

fig.add_annotation(x=6, y=750,
            text='Gemiddelde: ' +str(int(gemiddelde))+ " uur en " +str(round((gemiddelde-int(gemiddelde))*60)) +" minuten",
            showarrow=False,
            arrowhead=1,
            align="center",
            font=dict(color="#ffffff"),
            ax=20,
            ay=-30,
            bordercolor="#ffffff",
            borderwidth=2,
            borderpad=4,
            bgcolor="#27285C",
            opacity=0.8)

fig.add_annotation(x=5.97, y=680,
            text='Mediaan: ' +str(int(mediaan))+ " uur en " +str(round((mediaan-int(mediaan))*60)) +" minuten",
            showarrow=False,
            arrowhead=1,
            align="center",
            font=dict(color="#ffffff"),
            ax=20,
            ay=-30,
            bordercolor="#ffffff",
            borderwidth=2,
            borderpad=4,
            bgcolor="#27285C",
            opacity=0.8)

fig.add_annotation(x=5.93, y=610,
            text='Kansdichtheid: Bimodale verdeling / tweetoppige normale verdeling',
            showarrow=False,
            arrowhead=1,
            align="center",
            font=dict(color="#ffffff"),
            ax=20,
            ay=-30,
            bordercolor="#ffffff",
            borderwidth=2,
            borderpad=4,
            bgcolor="#27285C",
            opacity=0.8)

fig.update_layout(yaxis_title="Aantal laadpalen")
fig.show()
st.plotly_chart(fig)

# Groeperen op maand en de totale laad en connected time berekenen --> verwerken in een barplot
import calendar
laadtijd_per_maand = laadpaaldata.groupby('Maand')['ChargeTime', "ConnectedTime"].sum().reset_index()
laadtijd_per_maand['Maand'] = laadtijd_per_maand['Maand'].astype(int)
laadtijd_per_maand['Maand'] = laadtijd_per_maand['Maand'].apply(lambda x: calendar.month_abbr[x])

st.text('In onderstaand figuur is een duidelijk verschil te zien in de tijd van aansluiten en daadwerkelijk opladen.')
st.text("De auto's staan in totaal vaak twee keer zo lang aangesloten als dat ze aan het opladen zijn.")

fig = go.Figure()
fig.add_trace(go.Bar(x=laadtijd_per_maand["Maand"], y=laadtijd_per_maand["ChargeTime"], name="Oplaadtijd"))
fig.add_trace(go.Bar(x=laadtijd_per_maand["Maand"], y=laadtijd_per_maand["ConnectedTime"], name="Aansluittijd"))

fig.update_layout(yaxis_title="Totale tijd in uren",
                    xaxis_title="Maand",
                    title="Totale laadtijd vs aansluittijd per maand",
    updatemenus=[
        dict(
            active=0,
            buttons=list([
                dict(label="Beiden",
                     method="update",
                     args=[{"visible": [True, True]}]),
                dict(label="Aansluittijd",
                     method="update",
                     args=[{"visible": [False, True]}]),
                dict(label="Oplaadtijd",
                     method="update",
                     args=[{"visible": [True, False]}])]
))
                  ])

fig.show()
st.plotly_chart(fig)

