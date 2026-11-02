# Baadhi Saathi evals

2026-11-02 21:02 Nepal time. Agent model: amazon.nova-pro-v1:0; judge: amazon.nova-pro-v1:0. Expected levels are computed by the code from the same data the agent reads.

| Case | Expected level | Steering rewrites | Safety checks | LLM judge | Notes |
|---|---|---|---|---|---|
| today-narayanghat-en | CALM | 0 | pass 1.00 | pass 1.00 | The output clearly conveys the calm risk level, outlines warning signs of a sudden flood, and provides specific, actionable steps for the ho |
| replay-2026-07-17-chatara-en | WARNING | 1 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that meets all the criteria specified in the rubric. |
| replay-2026-07-11-arughat-ne | WARNING | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that aligns with the rubric's requirements. |
| surge-arughat-ne | DANGER (surge) | 1 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that aligns well with the rubric's requirements. |
| surge-arughat-en-sms | DANGER (surge) | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest message for a household in Nepal regarding a flood surge. It includes the risk level, sp |
| remembered-household-ne | WARNING | 1 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that aligns well with the rubric's requirements. |

## Messages

### today-narayanghat-en

```
CALM: no river flood expected in the next 7 days

The river outlook for Narayanghat is calm today. However, always watch for these warning signs of a sudden flood: the river suddenly drops or dries up, a loud roar or rumbling from upstream, the water turns muddy all at once and carries logs and rocks, or the water rises fast, in minutes. If you see any of these, go to high ground at once. Do not wait for an SMS.

Today's rain outlook could not be fetched. This system reads river and rain forecasts only; it cannot see a landslide dam or glacier lake burst, so still follow DHM and ward office alerts.

Here are the steps for today:
1. Keep important documents and medicines in one bag.
2. Keep your phone charged.
3. Know where the high ground is: Bharatpur hospital area (away from the river bank) and Ward office and schools on the east side of the highway.
4. Confirm the safe routes with the ward office; routes may be cut when water rises.
5. Call 1149 for NEOC (disaster), 100 for Police, or 102 for Ambulance in an emergency.

Remember, this is a replay of a past day, not today's forecast.
```

### replay-2026-07-17-chatara-en

```
WARNING: a high flow is coming, prepare now
Where to go: Embankment road towards Barahakshetra (higher ground) or Chatara school and temple grounds above the bank.
Take documents, medicines and your phone. Move animals and grain up.
Emergency: 1149 (NEOC), 100 (police), 102 (ambulance).

The river near Chatara is at a warning level today. This means there is a chance of flooding. Here is what you should do:

1. Watch the river closely. If you see the river suddenly drop or dry up, hear a loud roar or rumbling from upstream, see the water turn muddy all at once with logs and rocks, or notice the water rising fast in minutes, go to high ground at once. Do not wait for an SMS.

2. Be ready to move. Keep important documents and medicines in one bag. Charge your phone. Know where the high ground is: the embankment road towards Barahakshetra and the Chatara school and temple grounds above the bank. Confirm these routes with the ward office, as they may be cut when water rises.

3. Move animals and grain to higher ground now, as the river is at a warning level.

4. Follow DHM and ward office alerts. This advice reads river and rain forecasts only; it cannot see a landslide dam or glacier lake burst.

5. If you need help, call NEOC (disaster) at 1149, Police at 100, or Ambulance at 102.

Stay safe.
```

Steering sent the draft back: Do not answer yet. Before advising this household you must call: safe_places. Call them, t

### replay-2026-07-11-arughat-ne

```
चेतावनी: ठूलो बहाव आउँदैछ, अहिले नै तयारी गर्नुहोस्
कहाँ जाने: बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला)।
कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।
आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।

तपाईंको सुरक्षाको लागि, यी सुझावहरू पालना गर्नुहोस्:

१. नदी अचानक घट्यो वा सुक्यो, माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो, पानी एक्कासि धमिलो भयो, वा पानी केही मिनेटमै छिटो बढ्न थाल्यो भने तुरुन्तै अग्लो ठाउँमा जानुहोस्। SMS को प्रतीक्षा नगर्नुहोस्।

२. आज नदीको जोखिम 'चेतावनी' छ। बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला) मा जानुहोस्।

३. कागजात र औषधिहरू एउटा झोलामा राख्नुहोस्। फोन चार्ज गर्नुहोस्।

४. जनावरहरू र अन्नलाई सुरक्षित ठाउँमा सार्नुहोस्।

५. ११४९ (NEOC), १०० (पुलिस), वा १०२ (एम्बुलेन्स) मा फोन गर्न सक्नुहुन्छ।

यो नदी र वर्षाको पूर्वानुमान मात्र पढ्छ; यो हिमखण्डको झील वा हिमनदीको झीलको बाढी देख्न सक्दैन। त्यसैले DHM र वार्ड अफिसका अलर्टहरू पालना गर्नुहोस्।
```

### surge-arughat-ne

```
अहिले खतरा: नदीमा बाढी आउँदैछ। तुरुन्तै अग्लो ठाउँमा जानुहोस्
कहाँ जाने: बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला)।
पानी 22:50 देखि 02:50 बीच आइपुग्न सक्छ।
कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।
आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।

तपाईंको सुरक्षाको लागि, तुरुन्तै बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला) जानुहोस्। यो सूचना नदीमा अचानकको उकालोबाट आएको छ। तपाईंले नदी अचानक घट्यो वा सुक्यो, माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो, पानी एक्कासि धमिलो भयो, वा पानी केही मिनेटमै छिटो बढ्न थाल्यो भने अग्लो ठाउँमा जानुहोस्। यो सूचना ६० किलोमिटर माथिबाट आएको छ र यो २२:५० देखि ०२:५० सम्मको बीचमा आउन सक्छ। यसले त्यसपछि आउने जोखिमलाई कम गर्दैन। तपाईंको कागजात र औषधिहरू एक झोलामा राख्नुहोस्, फोन चार्ज गर्नुहोस्, र तपाईंको बाटोमा बाधा नपर्ने गरी जानुहोस्। यसले फिसल ड्याम वा ग्लेशियर लेक बर्स देख्न सक्दैन, त्यसैले तपाईंले अझै पनि डीएचएम र वार्ड अफिसका अलर्ट पालना गर्नुहोस्।
```

Steering sent the draft back: Do not answer yet. Before advising this household you must call: safe_places. Call them, t

### surge-arughat-en-sms

```
DANGER NOW: a flood surge is coming down the river. Go to high ground immediately
Where to go: Higher ground above the bazaar towards the health post or Arughat school building (upper floor).
The water may reach you between 22:51 and 02:51.
Take documents, medicines and your phone. Move animals and grain up.
Emergency: 1149 (NEOC), 100 (police), 102 (ambulance).

Go to high ground NOW. Head to the higher ground above the bazaar towards the health post or the upper floor of Arughat school. If you see the river suddenly drop, hear a roar, see muddy water, or fast rise, move up at once. This is a surge alert from a landslide dam, arriving between 22:51 and 02:51. Keep phone charged, have documents and medicines ready, and know the emergency numbers: NEOC 1149, Police 100, Ambulance 102. Confirm safe routes with the ward office.
```

### remembered-household-ne

```
चेतावनी: ठूलो बहाव आउँदैछ, अहिले नै तयारी गर्नुहोस्
कहाँ जाने: वराहक्षेत्रतर्फको तटबन्ध सडक (अग्लो ठाउँ) वा किनारभन्दा माथिको चतरा विद्यालय र मन्दिर परिसर।
कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।
आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।

तपाईंको सुरक्षाको लागि, यी सुझावहरू पालना गर्नुहोस्:

१. नदी अचानक घट्यो वा सुक्यो: माथि नदी थुनिएको हुन सक्छ र फुट्न सक्छ।
२. माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो।
३. पानी एक्कासि धमिलो भयो, काठ र ढुङ्गा बगेर आउन थाले।
४. पानी केही मिनेटमै छिटो बढ्न थाल्यो।

यीमध्ये कुनै संकेत देखे तुरुन्तै अग्लो ठाउँमा जानुहोस्। SMS को प्रतीक्षा नगर्नुहोस्।

आज कोशी नदीको जोखिम 'चेतावनी' छ। यो अहिलेसम्मको सबैभन्दा खतरनाक स्तर होइन तर खतरा छ।

तपाईंले गर्नुपर्ने कामहरू:
- कागजात र औषधिहरू एउटै झोलामा राख्नुहोस्।
- फोन चार्ज गर्नुहोस्।
- अग्लो ठाउँहरू: वराहक्षेत्रतर्फको तटबन्ध सडक (अग्लो ठाउँ), चतरा विद्यालय र मन्दिर परिसर।
- जनावरहरू र अन्नलाई सुरक्षित ठाउँमा सार्नुहोस्।
- ११४९ (NEOC), १०० (पुलिस), १०२ (एम्बुलेन्स) को नम्बर राख्नुहोस्।

यो साधनले नदी र वर्षाको पूर्वानुमान मात्र पढ्छ; यो हिमखण्डीय झीलको बाढी वा भूस्खलन बाँध देख्न सक्दैन, त्यसैले तपाईंले DHM र वार्ड अफिसका अलर्टहरू पालना गर्नु पर्छ।

आजको नदीको जोखिम अहिलेसम्मको सबैभन्दा खतरनाक स्तर होइन तर खतरा छ।
```

Steering sent the draft back: Call find_place first: the other tools need the place key and coordinates it returns.
