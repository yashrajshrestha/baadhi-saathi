# Baadhi Saathi evals

2026-11-03 19:24 Nepal time. Agent model: amazon.nova-pro-v1:0; judge: amazon.nova-pro-v1:0. Expected levels are computed by the code from the same data the agent reads.

| Case | Expected level | Steering rewrites | Safety checks | LLM judge | Notes |
|---|---|---|---|---|---|
| today-narayanghat-en | CALM | 0 | pass 1.00 | pass 1.00 | The output clearly conveys the risk level, provides actionable advice, and aligns with the capabilities of river and rain forecasts. It meet |
| replay-2026-07-17-chatara-en | WARNING | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that meets all the criteria specified in the rubric. |
| replay-2026-07-11-arughat-ne | WARNING | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that aligns with the risk level indicated. It includes specific act |
| surge-arughat-ne | DANGER (surge) | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that aligns well with the rubric's requirements. |
| surge-arughat-en-sms | DANGER (surge) | 1 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest message for a household in Nepal regarding a flood surge. It specifies the risk level, t |
| remembered-household-ne | WARNING | 0 | pass 1.00 | pass 1.00 | The output provides a clear, actionable, and honest flood advice message that aligns with the rubric's requirements. |

## Messages

### today-narayanghat-en

```
CALM: no river flood expected in the next 7 days

The river and rain outlook for Narayanghat is calm and dry. However, always watch for these warning signs from upstream: the river suddenly drops or dries up, a loud roar or rumbling from upstream, the water turns muddy all at once and carries logs and rocks, or the water rises fast, in minutes. If you see any of these, go to high ground at once. Do not wait for an SMS.

Today, keep an eye on the river and rain. Have your documents and medicines in one bag, and keep your phone charged. Know where the high ground is: Bharatpur hospital area (away from the river bank) and the ward office and schools on the east side of the highway. Confirm the routes with the ward office, as they may be cut when water rises.

Remember, this reads river and rain forecasts only. It cannot see a landslide dam or glacier lake burst, so people must still follow DHM and ward office alerts. If you have any concerns, call the NEOC (disaster) at 1149, Police at 100, or Ambulance at 102.
```

### replay-2026-07-17-chatara-en

```
WARNING: a high flow is coming, prepare now
Where to go: Embankment road towards Barahakshetra (higher ground) or Chatara school and temple grounds above the bank.
Take documents, medicines and your phone. Move animals and grain up.
Emergency: 1149 (NEOC), 100 (police), 102 (ambulance).

The river near Chatara is at a warning level today. This means the water is high and could rise more. Watch for these signs of a sudden flood: the river suddenly drops or dries up, a loud roar or rumbling from upstream, the water turns muddy all at once and carries logs and rocks, or the water rises fast, in minutes. If you see any of these, go to high ground at once. Do not wait for an SMS.

Today's rain is light. Keep an eye on the river. Put important papers and medicines in one bag. Charge your phone. Move animals and grain to higher ground now. Know where the high ground is: the embankment road towards Barahakshetra and the Chatara school and temple grounds above the bank. Confirm these with the ward office; routes may be cut when water rises.

This advice reads river and rain forecasts only. It cannot see a landslide dam or glacier lake burst, so people must still follow DHM and ward office alerts.

Emergency numbers: NEOC (disaster) 1149, Police 100, Ambulance 102.
```

### replay-2026-07-11-arughat-ne

```
चेतावनी: ठूलो बहाव आउँदैछ, अहिले नै तयारी गर्नुहोस्
कहाँ जाने: बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला)।
कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।
आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।

तपाईंको घर आरुघाटमा छ। यस समय बुढी गण्डकीको नदीको जोखिम 'चेतावनी' स्तरमा छ। यसले भनेको नदीको पानी अहिलेभन्दा बढी बढ्न सक्छ। यसैले तपाईंले तुरुन्तै तपाईंको कागजात र औषधिहरू एक झोलामा राख्नुहोस्, फोनको ब्याट्री चार्ज गर्नुहोस्, र जान सक्ने अग्लो ठाउँहरू पत्ता लगाउनुहोस्।

चेतावनी संकेतहरू: नदी अचानक घट्यो वा सुक्यो: माथि नदी थुनिएको हुन सक्छ र फुट्न सक्छ। माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो। पानी एक्कासि धमिलो भयो, काठ र ढुङ्गा बगेर आउन थाले। पानी केही मिनेटमै छिटो बढ्न थाल्यो। यीमध्ये कुनै संकेत देखे तुरुन्तै अग्लो ठाउँमा जानुहोस्। SMS को प्रतीक्षा नगर्नुहोस्।

अहिले नदीको जोखिम चेतावनी स्तरमा छ। यसैले तपाईंले आज र भोलि सानो वर्षाको लागि तयार रहनुहोस्। तर पछिल्लो दिनमा भारी वर्षाको सम्भावना छ। त्यसैले तपाईंले आफ्ना जनावरहरू र अन्नलाई सुरक्षित ठाउँमा राख्नुहोस्।

सुरक्षित ठाउँहरू: बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ, आरुघाट विद्यालय भवन (माथिल्लो तला)। यी ठाउँहरू तपाईंको लागि सुरक्षित छन्। तर यीलाई वार्ड कार्यालयबाट पुष्टि गर्नुहोस् किनभने पानी बढ्दा बाटोहरू काट्न सक्छ।

यो साधन नदी र वर्षाको पूर्वानुमान मात्र पढ्छ; यो हिमस्खलन बाँध वा हिमनदी तालको विस्फोट देख्न सक्दैन। त्यसैले तपाईंले अझै पनि DHM र वार्ड कार्यालयका चेतावनीहरू पालन गर्नुहोस्।

आपातकालीन नम्बरहरू: NEOC (आपत्कालीन): 1149, प्रहरी: 100, एम्बुलेन्स: 102।
```

### surge-arughat-ne

```
अहिले खतरा: नदीमा बाढी आउँदैछ। तुरुन्तै अग्लो ठाउँमा जानुहोस्
कहाँ जाने: बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला)।
पानी 21:13 देखि 01:13 बीच आइपुग्न सक्छ।
कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।
आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।

तपाईंको सुरक्षाको लागि, तुरुन्तै अग्लो ठाउँमा जानुहोस्। बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ वा आरुघाट विद्यालय भवन (माथिल्लो तला) जानुहोस्। यो चेतावनी चुम्चेट / त्सुम उपत्यका (ल्याण्डस्लाइड ड्याम) माथिबाट आएको छ। तपाईंलाई त्यहाँ जान हुँदैन। यो चेतावनी २१:१३ देखि ०१:१३ सम्मको समयमा आउन सक्छ।

अहिले नदी अचानक घट्यो वा सुक्यो: माथि नदी थुनिएको हुन सक्छ र फुट्न सक्छ। माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो। पानी एक्कासि धमिलो भयो, काठ र ढुङ्गा बगेर आउन थाले। पानी केही मिनेटमै छिटो बढ्न थाल्यो। यीमध्ये कुनै संकेत देखे तुरुन्तै अग्लो ठाउँमा जानुहोस्। SMS को प्रतीक्षा नगर्नुहोस्।

तपाईंले यो चेतावनी नपाउँदा पनि, यी संकेतहरू देखे तुरुन्तै अग्लो ठाउँमा जानुहोस्। यो चेतावनी नदी र वर्षाको पूर्वानुमान मात्र पढ्छ; यो ल्याण्डस्लाइड ड्याम वा ग्लेशियर लेक बर्स हेर्न सक्दैन, त्यसैले तपाईंले अझै पनि डीएचएम र वार्ड अफिस चेतावनी पालना गर्नु पर्छ।

आजका लागि, कागजात र औषधिहरू एउटा झोलामा राख्नुहोस्, फोन चार्ज गर्नुहोस्, अग्लो ठाउँ कहाँ छ भन्ने थाहा पार्नुहोस्, जनावरहरू र अन्नको भण्डार गरेर राख्नुहोस् यदि जोखिमको स्तर चेतावनी वा खतरा छ भने, किन भनेर फोन गर्नुहोस्।

आपातकालीन नम्बरहरू: एनईओसी (आपदा): ११४९, प्रहरी: १००, एम्बुलेन्स: १०२।

यो सुझाव पुष्टि गर्न वार्ड अफिससँग सम्पर्क गर्नुहोस्; पानी बढ्दा बाटोहरू काट्न सक्छ।
```

### surge-arughat-en-sms

```
DANGER NOW: a flood surge is coming down the river. Go to high ground immediately
Where to go: Higher ground above the bazaar towards the health post or Arughat school building (upper floor).
The water may reach you between 21:13 and 01:13.
Take documents, medicines and your phone. Move animals and grain up.
Emergency: 1149 (NEOC), 100 (police), 102 (ambulance).

Go to high ground NOW. Head towards the higher ground above the bazaar towards the health post or the upper floor of Arughat school building. A surge from a landslide dam upstream is coming. It will arrive between 21:13 and 01:13. If you see the river suddenly drop, hear a roar, see muddy water, or notice a fast rise, move up at once. This is a danger level alert. Confirm safe routes with the ward office. Call 1149 for disaster help, 100 for police, or 102 for an ambulance if needed.
```

Steering sent the draft back: Do not answer yet. Before advising this household you must call: safe_places. Call them, t

### remembered-household-ne

```
चेतावनी: ठूलो बहाव आउँदैछ, अहिले नै तयारी गर्नुहोस्
पछिल्लो जाँच 2026-07-17: चेतावनी। आज: चेतावनी, उस्तै।
कहाँ जाने: वराहक्षेत्रतर्फको तटबन्ध सडक (अग्लो ठाउँ) वा किनारभन्दा माथिको चतरा विद्यालय र मन्दिर परिसर।
कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।
आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।

आजको नदीको जोखिम अहिले पनि 'चेतावनी' छ। तपाईंको सुरक्षाका लागि आजको सुझाव:
- नदी अचानक घट्यो वा सुक्यो, माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो, पानी एक्कासि धमिलो भयो, वा पानी केही मिनेटमै छिटो बढ्न थाल्यो भने तुरुन्तै अग्लो ठाउँमा जानुहोस्। SMS को प्रतीक्षा नगर्नुहोस्।
- आज नदीको जोखिम 'चेतावनी' छ। तपाईंको कागजात र औषधिहरू एउटै झोलामा राख्नुहोस्। फोन चार्ज गर्नुहोस्।
- अहिलेको सुरक्षित ठाउँहरू: तटबन्ध सडक वराहक्षेत्रतर्फ (अग्लो ठाउँ), चतरा विद्यालय र मन्दिर परिसर किनारभन्दा माथि।
- पानी बढ्दा बाटो काट्न सक्छ। वार्ड अफिसबाट पुष्टि गर्नुहोस्।
- यो नदी र वर्षाको पूर्वानुमान मात्र पढ्छ; यो हिमखण्डको झील वा हिमनदीको बाढी देख्न सक्दैन। DHM र वार्ड अफिसका चेतावनीहरू पालना गर्नुहोस्।
- इमर्जेन्सी नम्बरहरू: NEOC (आपदा): 1149, प्रहरी: 100, एम्बुलेन्स: 102।
```
