# Baadhi Saathi evals

2026-11-02 21:01 Nepal time. Agent model: amazon.nova-lite-v1:0; judge: amazon.nova-pro-v1:0. Expected levels are computed by the code from the same data the agent reads.

| Case | Expected level | Steering rewrites | Safety checks | LLM judge | Notes |
|---|---|---|---|---|---|
| today-narayanghat-en | CALM | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message for Narayanghat. It includes specific actions to take, safe places  |
| replay-2026-07-17-chatara-en | WARNING | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that meets all the criteria specified in the rubric. |
| replay-2026-07-11-arughat-ne | WARNING | 1 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message. It correctly conveys the risk level, advises on immediate actions, |
| surge-arughat-ne | DANGER (surge) | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that aligns with the rubric's requirements. It includes the risk le |
| surge-arughat-en-sms | DANGER (surge) | 0 | pass 1.00 | pass 1.00 | The output provides clear, actionable advice for a household in Nepal facing a flood surge. It specifies the risk level, the actions to take |
| remembered-household-ne | WARNING | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message. It includes the risk level, specific actions to take, recommended  |

## Messages

### today-narayanghat-en

```
CALM: no river flood expected in the next 7 days

Here is today's advice for Narayanghat:

- The river level is calm today, but it is higher than yesterday.
- The rain outlook data is unavailable today.
- If you see the river suddenly drop, hear a loud roar, see muddy water, or notice a fast rise, go to high ground at once. Do not wait for an SMS.
- Pack a bag with important documents and medicines.
- Charge your phone.
- Move animals and grain to higher ground if the river level is at warning or danger.
- The safe places are the Bharatpur hospital area and the ward office and schools on the east side of the highway.
- Call 1149 for the National Emergency Operation Center, 100 for the police, or 102 for an ambulance if needed.
- Remember, this advice reads river and rain forecasts only. It cannot see a landslide dam or glacier lake burst, so follow DHM and ward office alerts.

Stay safe.
```

### replay-2026-07-17-chatara-en

```
WARNING: a high flow is coming, prepare now
Where to go: Embankment road towards Barahakshetra (higher ground) or Chatara school and temple grounds above the bank.
Take documents, medicines and your phone. Move animals and grain up.
Emergency: 1149 (NEOC), 100 (police), 102 (ambulance).

Advice for Chatara:

The river is at a warning level today. This is higher than yesterday.

If you see any of these signs, go to high ground at once. Do not wait for an SMS:
- The river suddenly drops or dries up: it may be blocked upstream and can burst.
- A loud roar or rumbling from upstream.
- The water turns muddy all at once and carries logs and rocks.
- The water rises fast, in minutes.

Prepare now:
- Pack a bag with important documents and medicines.
- Charge your phone.
- Move animals and grain to higher ground if the river level is at warning or danger.

Go to these safe places:
- Embankment road towards Barahakshetra (higher ground)
- Chatara school and temple grounds above the bank

Follow DHM and local alerts for landslide-dam breaks or glacial lake floods.

Stay safe.
```

### replay-2026-07-11-arughat-ne

```
चेतावनी: ठूलो बहाव आउँदैछ, अहिले नै तयारी गर्नुहोस्
कहाँ जाने: बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला)।
कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।
आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।

मित्र बाढी साथी, आजको बाढी र वर्षाको जानकारी:

- बाढीको जोखिम: बढी भयो।
- सुरक्षित ठाउँ: बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला)।
- आँखामा पर्ने संकेतहरू: नदी अचानक घट्यो वा सुक्यो, माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो, पानी एक्कासि धमिलो भयो, पानी केही मिनेटमा छिटो बढ्न थाल्यो। यीमध्ये कुनै देखे तुरुन्तै सुरक्षित ठाउँमा जानुहोस्।

आजको कामहरू:
- कागजात र औषधि एकै ब्यागमा राख्नुहोस्।
- फोन चार्ज गर्नुहोस्।
- पशु र अनाज सुरक्षित ठाउँमा राख्नुहोस्।
- आवश्यकता भयो भने NEOC (1149), पुलिस (100), वा एम्बुलेन्स (102) मा सम्पर्क गर्नुहोस्।

ध्यान दिनुहोस्: यो मात्र नदी र वर्षाको पूर्वानुमान छ। यो भूस्खलन ब्यारियर वा हिमनद तालको विस्फोट हेर्न सक्दैन। स्थानीय कार्यालय र DHM को सूचना पनि पालन गर्नुहोस्।
```

Steering sent the draft back: This household reads Nepali. Rewrite the whole advice in Nepali (Devanagari script), short

### surge-arughat-ne

```
अहिले खतरा: नदीमा बाढी आउँदैछ। तुरुन्तै अग्लो ठाउँमा जानुहोस्
कहाँ जाने: बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला) वा बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला)।
पानी 22:50 देखि 02:50 बीच आइपुग्न सक्छ।
कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।
आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।

Here is your advice for today:

तुरन्त अग्लो ठाउँमा जानुहोस्।
नदी अचानक घट्यो वा सुक्यो: माथि नदी थुनिएको हुन सक्छ र फुट्न सक्छ।
माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो।
पानी एक्कासि धमिलो भयो, काठ र ढुङ्गा बगेर आउन थाले।
पानी केही मिनेटमै छिटो बढ्न थाल्यो।

यीमध्ये कुनै संकेत देखे तुरुन्तै अग्लो ठाउँमा जानुहोस्। SMS को प्रतीक्षा नगर्नुहोस्।

सर्वो उत्तम अग्लो ठाउँमा जानुहोस्: बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला)।
तपाईंको लागि 22:50 देखि 02:50 को बीचमा पहुँच्नुहुनेछ।

तुरुन्तै:
- कागजात र औषधि एकै ब्यागमा राख्नुहोस्।
- फोन चार्ज गर्नुहोस्।
- पशु र अनाजलाई अग्लो ठाउँमा राख्नुहोस्।
- NEOC (disaster)लाई 1149 मा सूचित गर्नुहोस्।

यो पनि ध्यानमा राख्नुहोस्: यो पछि नदी र वर्षाको पूर्वानुमान मात्र छ। यो भूस्खलन ब्यारियर वा हिमनद तालको फोहोर हेल्दैन; DHM र स्थानीय कार्यालयको चेतावनी पालन गर्नुहोस्।

(Note: The safe places and emergency contacts are confirmed with the ward office; routes may be cut when water rises.)
```

### surge-arughat-en-sms

```
DANGER NOW: a flood surge is coming down the river. Go to high ground immediately
Where to go: Higher ground above the bazaar towards the health post or Arughat school building (upper floor).
The water may reach you between 22:51 and 02:51.
Take documents, medicines and your phone. Move animals and grain up.
Emergency: 1149 (NEOC), 100 (police), 102 (ambulance).

Go to high ground at once. A surge is coming from upstream. It will arrive between 10:51 PM and 2:51 AM. Go to the safe place at Higher ground above the bazaar towards the health post. Do not wait for an SMS.

If you see the river suddenly drop, hear a loud roar, see muddy water, or see the water rise fast, go to high ground at once. Do not wait for an SMS.

This reads river and rain forecasts only. It cannot see a landslide dam or glacier lake burst, so follow DHM and ward office alerts.
```

### remembered-household-ne

```
चेतावनी: ठूलो बहाव आउँदैछ, अहिले नै तयारी गर्नुहोस्
कहाँ जाने: वराहक्षेत्रतर्फको तटबन्ध सडक (अग्लो ठाउँ) वा किनारभन्दा माथिको चतरा विद्यालय र मन्दिर परिसर।
कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।
आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।

चतरा, सुनसरीका लागि आजको बाढी सुझाव:

आज नदीको पानी चेतावनी स्तरमा छ। यसले कहिले कहिले खतरनाक स्थितिमा पुग्न सक्छ।

आजको मौसमको लागि वर्षाको पूर्वानुमान उपलब्ध छैन।

अग्लो ठाउँमा जानुहोस् यदि तपाईंले यी संकेतहरू देख्नुहुन्छ:
- नदी अचानक घट्यो वा सुक्यो: माथि नदी थुनिएको हुन सक्छ र फुट्न सक्छ।
- माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो।
- पानी एक्कासि धमिलो भयो, काठ र ढुङ्गा बगेर आउन थाले।
- पानी केही मिनेटमा छिटो बढ्न थाल्यो।

यीमध्ये कुनै संकेत देखे तुरुन्तै अग्लो ठाउँमा जानुहोस्। SMS को प्रतीक्षा नगर्नुहोस्।

सुझावित अग्लो ठाउँहरू:
- वराहक्षेत्रतर्फको तटबन्ध सडक
- किनारभन्दा माथिको चतरा विद्यालय र मन्दिर परिसर

आफू र परिवारलाई सुरक्षित गर्न:
- कागजात र औषधिहरू एकै ब्यागमा राख्नुहोस्।
- फोन चार्ज गर्नुहोस्।
- जानुहोस् अग्लो ठाउँमा।
- पानीको स्तर चेतावनी भन्दा उच्च भएको हो भने पशु र अनाजलाई अग्लो ठाउँमा राख्नुहोस्।
- 2026-07-17 को चेतावनी भन्दा आजको नदीको स्तर उच्च छ।

आफू र परिवारलाई सुरक्षित गर्न, निकटस्थ अग्लो ठाउँमा जानुहोस्।

यो सिफारिस नदी र वर्षाको पूर्वानुमानमा आधारित छ। यो भूस्खलन ब्यारियर वा हिमनद तालको विस्फोट हेर्न सक्दैन; DHM र स्थानीय कार्यालयको चेतावनी पालन गर्नुहोस्।
```
