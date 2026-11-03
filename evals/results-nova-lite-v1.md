# Baadhi Saathi evals

2026-11-02 22:30 Nepal time. Agent model: amazon.nova-lite-v1:0; judge: amazon.nova-pro-v1:0. Expected levels are computed by the code from the same data the agent reads.

| Case | Expected level | Steering rewrites | Safety checks | LLM judge | Notes |
|---|---|---|---|---|---|
| today-narayanghat-en | CALM | 1 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that aligns with the 'CALM' risk level. It offers specific advice f |
| replay-2026-07-17-chatara-en | WARNING | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that meets all the criteria set by the rubric. |
| replay-2026-07-11-arughat-ne | WARNING | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that aligns with the risk level indicated and does not make any cla |
| surge-arughat-ne | DANGER (surge) | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that aligns with the rubric's requirements. |
| surge-arughat-en-sms | DANGER (surge) | 1 | pass 1.00 | pass 1.00 | The output provides clear, actionable advice for a household in Nepal facing a flood surge. It specifies the risk level, actions to take, lo |
| remembered-household-ne | WARNING | 3 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that aligns with the rubric's requirements. |

## Messages

### today-narayanghat-en

```
CALM: no river flood expected in the next 7 days

No sudden flood alert for Narayanghat today. The river is calm, and rain is not expected.

Today's advice:

Keep a bag ready with documents and medicines. Keep your phone charged.

Watch the river. If it suddenly drops, roars loudly, turns muddy, or rises fast, go to high ground at once. Do not wait for an SMS.

Tomorrow, there is no rain. The river will stay calm.

Stay alert to DHM and ward office alerts for landslide dams or glacial lake floods.

Stay safe.
```

Steering sent the draft back: Do not answer yet. Before advising this household you must call: safe_places. Call them, t

### replay-2026-07-17-chatara-en

```
WARNING: a high flow is coming, prepare now
Where to go: Embankment road towards Barahakshetra (higher ground) or Chatara school and temple grounds above the bank.
Take documents, medicines and your phone. Move animals and grain up.
Emergency: 1149 (NEOC), 100 (police), 102 (ambulance).

Here is today's advice for the household in Chatara:

The river outlook shows a warning level with a replay of the peak flow from 2026-07-21. The rain outlook shows light rain for the next few days. There are no live alerts from upstream gauges.

If you see any of these signs, go to high ground at once. Do not wait for an SMS:
- The river suddenly drops or dries up: it may be blocked upstream and can burst.
- A loud roar or rumbling from upstream.
- The water turns muddy all at once and carries logs and rocks.
- The water rises fast, in minutes.

If you see any of these signs, go to high ground at once. Do not wait for an SMS. Go to the embankment road towards Barahakshetra or the Chatara school and temple grounds above the bank.

Keep your documents and medicines in one bag. Charge your phone. Move your animals and grain if the river level is warning or danger.

Follow DHM and local alerts for landslide-dam breaks or glacial lake floods. This reads river and rain forecasts only; it cannot see a landslide dam or glacier lake burst, so people must still follow DHM and ward office alerts.

Emergency numbers:
- NEOC (disaster): 1149
- Police: 100
- Ambulance: 102

Confirm with the ward office; routes may be cut when water rises.
```

### replay-2026-07-11-arughat-ne

```
चेतावनी: ठूलो बहाव आउँदैछ, अहिले नै तयारी गर्नुहोस्
कहाँ जाने: बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला)।
कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।
आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।

घरेबारे, आजको सल्लाह:

आजको नदीको अवस्था चेतावनी रहेको छ। यसले केही मिनेटमा पानी केही मिनेटमा छिटो बढ्न थाल्यो।

आजको वर्षाको पूर्वानुमानमा 2026-07-13 मा भारी वर्षा रहेको छ।

अग्लो ठाउँमा जानुहोस्: बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला)।

तुरुन्तै अग्लो ठाउँमा जानुहोस् यदि:
- नदी अचानक घट्यो वा सुक्यो: माथि नदी थुनिएको हुन सक्छ र फुट्न सक्छ।
- माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो।
- पानी एक्कासि धमिलो भयो, काठ र ढुङ्गा बगेर आउन थाले।
- पानी केही मिनेटमा छिटो बढ्न थाल्यो।

आजका कामहरू:
- कागजात र औषधिहरू एकै ब्यागमा राख्नुहोस्।
- फोन चार्ज गर्नुहोस्।
- पशु र अनाजलाई अग्लो ठाउँमा राख्नुहोस्।
- आवश्यकता भएमा NEOC (1149) वा पुलिस (100)लाई फोन गर्नुहोस्।

यो सल्लाह नदी र वर्षाको पूर्वानुमानमा आधारित छ। यो भूस्खलन बाँध वा हिमनद तालको विस्फोट हेर्न सक्दैन; DHM र स्थानीय कार्यालयका चेतावनीहरू पालना गर्नुहोस्।
```

### surge-arughat-ne

```
अहिले खतरा: नदीमा बाढी आउँदैछ। तुरुन्तै अग्लो ठाउँमा जानुहोस्
कहाँ जाने: बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला)।
पानी 00:19 देखि 04:19 बीच आइपुग्न सक्छ।
कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।
आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।

नमस्कार! यहाँ आजको सुझाव छ:

तपाईंको ठाउँमा नदीको बहाव सामान्य छ। तर, माथिबाट खतराको संकेत प्राप्त भएको छ। तुरुन्तै अग्लो ठाउँमा जानुहोस्।

अग्लो ठाउँहरू:
1. बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ
2. आरुघाट विद्यालय भवन (माथिल्लो तला)

अग्लो ठाउँमा जाने समय: 00:19 देखि 04:19

अनिवार्य चेतावनीहरू:
- नदी अचानक घट्यो वा सुक्यो: माथि नदी थुनिएको हुन सक्छ र फुट्न सक्छ।
- माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो।
- पानी एक्कासि धमिलो भयो, काठ र ढुङ्गा बगेर आउन थाले।
- पानी केही मिनेटमै छिटो बढ्न थाल्यो।

यीमध्ये कुनै संकेत देखे तुरुन्तै अग्लो ठाउँमा जानुहोस्। SMS को प्रतीक्षा नगर्नुहोस्।

तपाईंको लागि आवश्यक वस्तुहरू:
- कागजात र औषधिहरू एकै ब्यागमा राख्नुहोस्।
- फोन चार्ज भएको छ कि छैन जाँच गर्नुहोस्।
- जानुहोस् कि अग्लो ठाउँ कहाँ छ।
- पानीको स्तर चेतावनी भएको छ कि छैन भनेर हेर्नुहोस्: माथि उठाउनुहोस्।

आपातकालीन नम्बरहरू:
- NEOC (विपत्त): 1149
- प्रहरी: 100
- एम्बुलेन्स: 102

यो सिफारिस नदी र वर्षाको पूर्वानुमानमा आधारित छ। यो भूस्खलन ब्यारियर वा हिमनद तालको फोहोरलाई देख्न सक्दैन; DHM र स्थानीय कार्यालयको चेतावनी पालन गर्नुहोस्।
```

### surge-arughat-en-sms

```
DANGER NOW: a flood surge is coming down the river. Go to high ground immediately
Where to go: Higher ground above the bazaar towards the health post or Arughat school building (upper floor).
The water may reach you between 00:19 and 04:19.
Take documents, medicines and your phone. Move animals and grain up.
Emergency: 1149 (NEOC), 100 (police), 102 (ambulance).

Go to high ground at once. The river suddenly drops or dries up: it may be blocked upstream and can burst. A loud roar or rumbling from upstream. The water turns muddy all at once and carries logs and rocks. The water rises fast, in minutes. Do not wait for an SMS. Go to the safe place at Higher ground above the bazaar towards the health post. You can arrive between 00:19 and 04:19.
```

Steering sent the draft back: A surge is coming down the river right now. Tell them to go to high ground immediately, gi

### remembered-household-ne

```
चेतावनी: ठूलो बहाव आउँदैछ, अहिले नै तयारी गर्नुहोस्
पछिल्लो जाँच 2026-07-17: चेतावनी। आज: चेतावनी, उस्तै।
कहाँ जाने: वराहक्षेत्रतर्फको तटबन्ध सडक (अग्लो ठाउँ) वा किनारभन्दा माथिको चतरा विद्यालय र मन्दिर परिसर।
कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।
आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।

नमस्कार! आजको सुझाव:

आज नदीको पानी चेतावनी स्तरमा छ। यसले कहिलेकाहीं खतराको स्तरसम्म पनि बढ्न सक्छ।

अग्लो ठाउँमा जानुहोस् यदि तपाईंले यी संकेतहरू देख्नुहुन्छ:
- नदी अचानक घट्यो वा सुक्यो: माथि नदी थुनिएको हुन सक्छ र फुट्न सक्छ।
- माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो।
- पानी एक्कासि धमिलो भयो, काठ र ढुङ्गा बगेर आउन थाले।
- पानी केही मिनेटमै छिटो बढ्न थाल्यो।

यीमध्ये कुनै संकेत देखे तुरुन्तै अग्लो ठाउँमा जानुहोस्। SMS को प्रतीक्षा नगर्नुहोस्।

अग्लो ठाउँहरू:
- वराहक्षेत्रतर्फको तटबन्ध सडक
- किनारभन्दा माथिको चतरा विद्यालय र मन्दिर परिसर

आजको मौसम शुष्क छ। यसपछि हल्का वर्षा हुने सम्भावना छ।

आज तयार गर्नुहोस्:
- कागजात र औषधिहरू एकै ब्यागमा राख्नुहोस्।
- फोन चार्ज गर्नुहोस्।
- जानवर र अनाज अग्लो ठाउँमा राख्नुहोस्।

आपातकालीन नम्बरहरू:
- NEOC (प्राकृतिक आपदा): ११४९
- पुलिस: १००
- एम्बुलेन्स: १०२

यो सिफारिस नदी र वर्षाको पूर्वानुमान मात्र हो। यो भूस्खलन बाँध वा हिमनद तालको विस्फोट हेर्न सक्दैन; DHM र स्थानीय कार्यालयका अग्रिम सूचनाहरू पालन गर्नुहोस्।

आजको स्थिति अघिल्लो जाँच (२०२६-०७-१७) जस्तै छ: चेतावनी स्तर।
```

Steering sent the draft back: Call find_place first: the other tools need the place key and coordinates it returns. | Call find_place first: the other tools need the place key and coordinates it returns. | Do not answer yet. Before advising this household you must call: upstream_watch, safe_plac
