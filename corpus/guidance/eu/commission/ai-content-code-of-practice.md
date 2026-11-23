---
id: eu-commission-ai-content-cop-2026
title: Code of Practice on Transparency of AI-Generated Content
instrument: eu-commission-guidance
kind: curated_quotes
citation: Commission Code of Practice on Transparency of AI-Generated Content
source_uri: "https://ec.europa.eu/newsroom/dae/redirection/document/129555"
source_format: pdf
revision_id: Final, 10 June 2026
content_sha256: 685efee3f2b59ff73ada0275c0a57f05815fd56673ddd4758b8ead88e344cb88
last_fetched: 2026-11-23
language: en-GB
enforcement_status: guidance
---
# Code of Practice on Transparency of AI-Generated Content (curated quotes)

_The final Code of Practice drawn up under Article 50(7) of Regulation (EU) 2024/1689 (the AI Act) and published by the European Commission on 10 June 2026. Section 1 covers providers of generative AI systems under Article 50(2) and (5); Section 2 covers deployers under Article 50(4) and (5). The Code is voluntary: adherence does not constitute conclusive evidence of compliance. Curated quotes only; the complete Code, including its Annex 1 icons, is at the source URI. Glossary definitions are quoted from the Section 1 glossary._

_United Kingdom status: the AI Act is EU law and is not retained in the United Kingdom. The Code has no legal effect in the United Kingdom. It is mirrored because Article 2 applies the AI Act to providers placing AI systems on the Union market and to deployers and providers in a third country where the output is used in the Union. Review pending._

## Status of the Code

> a) to serve as a guiding document for demonstrating compliance with the obligations provided for in Article 50(2) and (5) AI Act, while recognising that adherence to the Code does not constitute conclusive evidence of compliance with these obligations; (Section 1, Objectives, point a)

> This Section of the Code applies to Signatories who are providers of generative AI systems falling within Article 2 and Article 50(2) AI Act, taking into account the scope of the legal obligations and relevant exceptions, as applicable. (Section 1, Commitments)

> In this Section, the terms “will”, “encouraged” and “may” should be interpreted in the following way:
>
> 1. ‘will’ is used for mandatory measures under the Code that need to be met for the Signatory to be compliant with Article 50(2) and (5) AI Act, and for which compliance will be monitored by competent market surveillance authorities;
>
> 2. ‘encouraged’ is used for optional measures under the Code that are not legally required and are purely voluntary, but are nevertheless recommended;
>
> 3. ‘may’ is used for optional measures under the Code that are not legally required and are purely voluntary or provide providers with flexibility on how to implement the respective measure or commitment. (Section 1, Commitments)

## Providers: machine-readable marking (Commitment 1)

> In order to fulfil their obligation under Article 50(2) AI Act to mark in a machine-readable manner the outputs of generative AI systems, including general-purpose AI systems, Signatories commit to implement a marking solution with regard to audio, image, video or text content, or any combination thereof, generated or manipulated by the AI system(s) which they place on the market or put into service in the Union. (Section 1, Commitment 1)

> Signatories will implement a marking solution that consists of at least one machine-readable marking technique, as detailed below, which, in conjunction with their respective detection mechanism, meets the level of effectiveness, reliability, robustness, and interoperability required by Article 50(2) AI Act and Commitment 3 of the Code. (Section 1, Measure 1.1)

> So long as no single marking technique can, under the state of the art, ensure by itself compliance with the four requirements in Article 50(2) AI Act of effectiveness, interoperability, robustness, and reliability for audio, images, video, and containerised text, in particular for content that can be disseminated online, Signatories will implement a multi-layered marking approach to ensure that the outputs of their generative AI systems are marked with at least two layers of machine-readable marking, as specified in Sub-measures 1.1.1 and 1.1.2 below. (Section 1, Measure 1.1)

> To enable a proportionate implementation of the above requirements, a single layer of marking will be considered sufficient in specific cases where a generative AI system is embedded in physical products capable of generating synthetic outputs in a technically controlled and closed environment mainly instructive in nature. This applies to the extent effective technical measures are embedded in the product to prevent the output from leaving the environment of the product, for example by being captured or exported and disseminated externally. Moreover, given that free-form text cannot transport metadata, a single-layer of marking as described in Sub-measure 1.1.2 is considered sufficient to comply with the requirements of Article 50(2) AI Act for this specific type of content. (Section 1, Measure 1.1)

> In the future, Signatories will also be able to demonstrate compliance with Article 50(2) AI Act through the use of alternative marking technique(s) (possibly a single marking technique), provided that they can prove to the competent market surveillance authorities, based on recognised performance evaluation methods and benchmarks, that their technique(s) achieve at least the same, if not superior, level of robustness, reliability, effectiveness, and interoperability, as required by Article 50(2) AI Act and Commitment 3 of the Code. Pending the emergence of recognised performance evaluation methods and benchmarks, and as specified in Measure 4.2, Signatories may demonstrate compliance through documented internal testing against the requirements in Commitment 3, subject to review by the competent market surveillance authorities. (Section 1, Measure 1.1)

> The marking techniques may be implemented at different stages of the value chain (e.g., by the provider of the AI system itself or by an upstream model provider) and may also be provided by third parties (in particular, technology providers specialised in marking techniques and detection mechanisms for AI transparency). Signatories may rely on those third-party technical solutions without prejudice to the Signatories’ own responsibility under the AI Act and the Code to ensure that the outputs of their AI systems are suitably and compliantly marked. (Section 1, Measure 1.1)

## Providers: digitally signed metadata

> If content is generated, manipulated or exported in a data format that supports attaching metadata (e.g., an audio, image, video, or containerised text), Signatories will record information in the metadata on whether the content is AI-generated or manipulated. (Section 1, Sub-measure 1.1.1)

> All recorded information will be digitally signed and time-stamped (on systems where time information is available) in a secure and tamper-evident manner. Signatories will adopt means for ensuring the secure usage of the signing certificates and the confidentiality of the associated private keys, except in circumstances where the deployment context does not permit the secure handling or provisioning of the key, for example in a local deployment scenario. (Section 1, Sub-measure 1.1.1)

> Signatories are encouraged to implement richer metadata in accordance with Measure 1.3., , without including privacy-sensitive or business-sensitive information. In cases where such information is strictly necessary or inserted upon request of an end-user, it will be compliant with applicable EU data protection law and is encouraged to be placed in a metadata placeholder separate from the AI transparency metadata. (Section 1, Sub-measure 1.1.1)

## Providers: imperceptible watermarking and the text threshold

> Signatories will ensure that AI-generated or manipulated content is marked with an imperceptible watermark, with the exception of very short text. For free-form text longer than 200 tokens, watermarking still needs to be applied, even though it may have lower reliability compared to that of watermarking very long text. To compensate for the potential lower reliability of watermarking for free-form text, access to the corresponding detection solution may be restricted to verified expert users as detailed in Sub-measure 2.1.2. (Section 1, Sub-measure 1.1.2)

> The imperceptible watermark will be embedded within the content in a manner that is difficult for it to be separated from the content. The watermark is intended to serve as a robust mechanism to complement the digitally signed metadata under Sub-measure 1.1.1. (Section 1, Sub-measure 1.1.2)

> A raw sequence of characters with no enclosing structure, schema, or container format. It is not bound to any metadata, layout rules, or encoding beyond basic character representation. Examples could be the text that is shown on a website or within a chat. (Section 1, Glossary, “Free-form text”)

> Text that is embedded within a structured file format or a container, where the content is organised according to specific rules defined by the format. The container may include metadata, layout information, and encoding details that influence how the text is stored, displayed, and processed. Examples include text inside PDFs, Word documents, or HTML files. (Section 1, Glossary, “Containerised text”)

> Text that is so short that in many cases it cannot be watermarked, even with a basic level of reliability. At the time of publication of the code, state-of-the-art techniques enable watermarking with at least a basic level of reliability of text as short as 200 tokens, with the expectation that this threshold will decrease as new methods become available. Until then, “very short text” should be understood as text shorter than 200 tokens. (Section 1, Glossary, “Very short text”)

## Providers: fingerprinting or logging

> Where appropriate and taking into account potential trade-offs related to privacy and security, as well as scalability challenges and costs, Signatories may implement as an optional supplementary measure fingerprinting or logging solutions for AI-generated or manipulated content which allow for checking whether content has been generated or manipulated by their AI system. For example, direct logging may be appropriate for text content, whereas fingerprinting approaches may be preferable for audio and visual content. (Section 1, Sub-measure 1.1.3)

> The use of such techniques may be a supplementary solution to meet the quality requirements specified in Article 50(2) AI Act and in Commitment 3 or to help reduce the cost of the detection mechanism outlined in Commitment 2. However, relying on fingerprinting or logging alone is not considered sufficient to meet the quality requirements specified in Article 50(2) AI Act and in Commitment 3. (Section 1, Sub-measure 1.1.3)

## Providers: non-removal of markings

> Without prejudice to the robustness requirement in Commitment 3, Signatories will make best efforts to preserve metadata markings on input data and content generated or manipulated by their AI system by applying the following cumulative measures:
>
> a) Signatories will, to the extent technically feasible and recognisable as per open standards, retain, and abstain from intentionally altering or removing, existing metadata markings, where such content is used as input and subsequently transformed by their AI system into an output. This does not affect good faith, legitimate processing where the modification, transformation or replacement of existing metadata is necessary to maintain accurate and functional information following downstream processing or specific legitimate processing, such as for security audits and research purposes.
>
> b) While Signatories recognise that downstream compliance and enforcement cannot be guaranteed, they will nevertheless include in the acceptable use policy, terms and conditions or the documentation accompanying their generative AI system a prohibition of the intentional removal of or tampering with metadata markings by deployers or any other third party. Exceptions to such a prohibition are the legitimate purposes referred to in point
>
> a). For AI systems and models provided under free and open-source licenses, it is sufficient for Signatories to alert users to this best practice in the documentation accompanying the AI system or model, without prejudice to the free and open-source nature of the license. (Section 1, Measure 1.2)

> Measures specified in point a) above do not imply the responsibility of the Signatory for third-party metadata markings, nor for compliance of third parties with the conditions specified in point b). (Section 1, Measure 1.2)

> Furthermore, Signatories will neither place or make available on the market, nor promote or advertise the use of tools whose purpose is to circumvent the machine-readable markings added to the AI-generated or manipulated content for transparency. (Section 1, Measure 1.2)

## Providers: provenance information and perceptible markings (optional)

> Signatories are encouraged to add or record relevant content provenance information within content generated or manipulated by their AI systems, in particular the name of the AI system, the company name of the AI provider, and a timestamp indicating when the content was generated or manipulated. Additionally, Signatories may also include the underlying AI model identifier and version number. (Section 1, Measure 1.3)

> In order to facilitate compliance of deployers of generative AI systems with their obligation to disclose deep fakes and AI-generated or manipulated published text pursuant to Article 50(4) AI Act, Signatories who are providers of generative AI systems that are capable of generating or manipulating such content are encouraged to provide an optional functionality in their system's interface and to implement an integrated option that allows deployers and other users to directly apply at their own discretion – upon generation of the output – a perceptible label in consistency with the Commitments and Measures in Section 2 of the Code. (Section 1, Measure 1.4)

> This measure is without prejudice to the responsibility of deployers who remain responsible for the disclosure of deep fakes and AI-generated or manipulated published text in a clear and distinguishable manner in accordance with Article 50(4) and (5) AI Act. (Section 1, Measure 1.4)

## Providers: detection (Commitment 2)

> In order to fulfil their obligations under Article 50(2) and (5) AI Act to ensure that the outputs of their AI system(s) are detectable as AI-generated or manipulated, Signatories commit to provide the means to enable the detection of the machine-readable markings present in audio, image, video or text content, or a combination thereof, as generated or manipulated by their AI system. Signatories also commit to ensure that the detection result is provided to the natural persons concerned in a clear, distinguishable and accessible manner. (Section 1, Commitment 2)

> Signatories will make available a detection solution, composed of one or more detection mechanisms, to enable deployers, users of their generative AI system, third-party integrators, end-users exposed to the content, and other legitimate parties (such as competent authorities, independent researchers, civil society and media organisations) to verify whether content has been generated or manipulated by their AI system based on the marking technique(s) implemented pursuant to Commitment 1. Signatories will ensure that the detection solution, in conjunction with the associated marking solution, meets the level of effectiveness, interoperability, robustness, and reliability required by Article 50(2) AI Act, Commitment 3 of the Code, and the following Sub-measures. (Section 1, Measure 2.1)

> The detection solution may be made available in the Union as one or more of the following: (i) a public, ideally standardised, specification allowing any third party to implement a detection mechanism; (ii) a piece of software (e.g., a standalone executable or library); (iii) a cloud-based service accessible to users in the Union through an API. When providing a public specification under point (i), Signatories are encouraged to provide a reference implementation. When providing a piece of software under point (ii), Signatories are encouraged to ensure that the version is portable on most operating systems (including, where technically feasible, mobile phone systems) and that the hardware requirements are limited, if any at all, to facilitate the local execution of the detection mechanism(s) on any general-purpose device. (Section 1, Sub-measure 2.1.1)

> Signatories will ensure that their detection solution includes a detection mechanism for each marking technique implemented in their generative AI system pursuant to Commitment 1. (Section 1, Sub-measure 2.1.1)

> Signatories will make the detection solution available free of charge. Signatories with fewer than 1,000,000 monthly users of their generative AI system, whose detection solution incurs substantial operational costs (in particular when it is provided for detection of watermarks as a cloud-based service), may charge a fee for the use of their detection solution (which will be reasonable, fair and proportionate to the overall operational costs of that solution) in cases where requests from a single user exceed a reasonable threshold due to large volume of requests. All Signatories will always provide free access to their detection solution, without any restriction on the volume of requests, to competent market surveillance authorities and other regulators, law enforcement authorities, media, fact-checkers, trusted flaggers, independent researchers, educational and research institutions, and civil society organisations. (Section 1, Sub-measure 2.1.1)

> Signatories will ensure access to their detection solution through a user interface appropriate for the audience of end-users that may eventually be exposed to the content generated or manipulated by their AI system. Where the general public may be exposed to the AI-generated or manipulated content, the detection solution will accordingly be made available to the general public. However, where there are safeguards to ensure that only a limited number of natural persons will be exposed to the AI-generated or manipulated content (e.g., AI systems in professional settings), and where there are effective safeguards to prevent further dissemination of the content to the general public, access to the detection solution may be restricted to those natural persons. (Section 1, Sub-measure 2.1.2)

> In their detection solution, Signatories may restrict access to detection mechanisms associated to watermarking techniques for free-form text to the extent that they have a lower level of reliability and robustness and that they may produce misleading or low-confidence results. However, the results of such detection mechanisms may still provide valuable information to verified expert end-users with a legitimate need, including competent market surveillance authorities, other regulators, law enforcement authorities, media, fact-checkers, trusted flaggers, independent researchers, educational and research organisations, and civil society organisations. Therefore, Signatories will ensure that access for these expert end-users is granted subject to appropriate access controls and safeguards. Any restriction to the access will be limited in time until more reliable and robust detection mechanisms have emerged and have been adopted as the state of the art for detection mechanisms for the watermarking of free-form text evolves. (Section 1, Sub-measure 2.1.2)

> Moreover, Signatories will ensure that the detection result of specific content submitted for detection can be downloaded upon request in a digitally signed format, including at least a hash of the content submitted for detection, a URL or other identifier of the detection solution, and a timestamp. (Section 1, Sub-measure 2.1.2)

> Signatories will ensure that the detection is compliant with EU privacy and data protection law. Without prejudice to applicable EU law, including EU privacy and data protection law, for any detection solution provided as a software or a service (fully or in part) that requires uploading content, Signatories will ensure: (Section 1, Sub-measure 2.1.3)

> (e) That the content is stored only for the duration of the detection and is permanently deleted immediately thereafter (i.e. with a ‘zero retention’ policy) provided that minimal data (such as traffic logs) may be retained for a limited period on a valid legal basis solely to ensure security and prevent abuse. In particular, Signatories will not retain a verbatim copy of the content and will delete it immediately after the detection. (Section 1, Sub-measure 2.1.3, point (e))

> In order to fulfil their obligation under Article 50(5) AI Act, Signatories will ensure that the detection results provided by their detection solution are presented in a way that is clear and easily comprehensible to natural persons exposed to the content generated or manipulated by their AI system and who want to verify its origin. (Section 1, Measure 2.3)

> Signatories will ensure that detection results indicate whether they are based on a metadata marking, a watermark marking, forensic detection or other techniques, to the extent technically feasible. (Section 1, Measure 2.3)

> Where applicable, Signatories will ensure that human interfaces used to present detection results are accessible to persons with disabilities in compliance with applicable accessibility requirements under Union law, in particular those laid down in Directive (EU) 2019/882 (the European Accessibility Act) and Directive (EU) 2016/2102 (the Web Accessibility Directive). (Section 1, Measure 2.3)

## Providers: quality requirements (Commitment 3)

> In order to fulfil their obligation under Article 50(2) AI Act to ensure the employed technical solutions for marking and detection of AI-generated or manipulated content are effective, interoperable, robust and reliable, as far as this is technically feasible and taking into account the specificities and limitations of various types of content, the costs of implementation and the generally acknowledged state of the art, Signatories commit to ensure that their marking and detection solutions comply with the quality requirements described in the following measures, holistically across all marking techniques employed rather than for each technique individually. (Section 1, Commitment 3)

> Signatories will implement marking and detection solutions which, together, maintain intended performance levels under varying conditions, covering both common alterations and adversarial attacks, to the extent technically feasible, and in alignment with the state of the art. This requirement does not apply to AI systems that are exceptionally subject only to one layer of metadata marking as specified in Measure 1.1. (Section 1, Measure 3.3)

> In the initial stage as of the entry into application of Article 50(2) AI Act, Signatories will:
>
> (a) adopt relevant established standards or best practices to implement metadata marking and detection, thereby enabling open detection of such markings;
>
> (b) provide public information to the Commission and relevant stakeholders on how to integrate and access detection solutions for the other type(s) of marking technique(s) that they have implemented in their AI system. To facilitate dissemination of such information, Signatories are encouraged to provide relevant information on their websites and to populate publicly available registries that may be created to streamline integrations. (Section 1, Measure 3.4)

> (c) work towards a minimum level of interoperability among detection solutions for watermarking that reduce burden and costs for the Signatories, while ensuring a more seamless access for end-users. More specifically, Signatories will implement an interoperability solution for their detection mechanisms by 2 February 2027 by implementing one or more of the following: (Section 1, Measure 3.4, point (c))

## Deployers: scope of the labelling commitments

> This Section of the Code applies only to Signatories in so far as they are deployers of AI systems that generate or manipulate image, audio or video content constituting a deep fake1 or text published with the purpose of informing the public on matters of public interest falling within the scope of Article 50(4) AI Act. Each reference below to “content”, “deep fake” or “published text” implies content that is i) AI-generated or manipulated and that qualifies as a deep fake under Article 3(60) AI Act (referred to as “deep fake”), or ii) AI-generated or manipulated text published with the purpose of informing the public on matters of public interest, without human review or editorial control and where no natural or legal person holds editorial responsibility for the publication of the content (referred to as “published text” or “text published on matters of public interest”). (Section 2, Commitments)

> A deep fake is defined in Article 3(60) AI Act as AI-generated or manipulated image, audio or video content that resembles existing persons, objects, places, entities or events and would falsely appear to a person to be authentic or truthful. (Section 2, Commitments, footnote 1)

> To fulfil their obligations under Article 50(4) and (5) AI Act, Signatories commit to ensure consistent and effective disclosure of the artificial origin of deep fakes or published text. Signatories commit to implement such disclosure through the available EU icon provided in Annex 1 of the Code or through an equivalent icon or label that complies with the design and placement specifications as described in the following measures. (Section 2, Commitment 1)

> Signatories may integrate the icon or equivalent label into their existing disclosure practices under applicable sectoral Union and national legislation or professional codes of conduct, to the extent that those practices comply with this Section of the Code and Article 50(4) and (5) AI Act. (Section 2, Commitment 1)

## Deployers: design of the icon or label

> Where visual disclosure is possible, Signatories will implement the following design specifications:
>
> a) The icon or equivalent label will comprise, as the main visual element, the capitalised acronym “AI” in the English language (e.g., an ‘AI’ icon), unless use of English is incompatible with applicable national laws on the use of languages in commercial or administrative matters in which case the acronym may be disclosed in the national language. The letters in the acronym will have the same vertical dimension. If resized, the proportions of the letters must be preserved. (Section 2, Measure 1.1)

> b) Additionally, Signatories are encouraged to supplement the acronym in the icon with information regarding whether the deep fake or published text is manipulated or generated with AI in an (interactive) second layer where this is technically implementable, in the icon or next to the icon (e.g., text indicating “modified” or “generated”, as illustrated in Annex 1). Signatories are furthermore encouraged to disclose in the (interactive) second layer what has been modified by the AI system (e.g., text or pictogram describing that a face has been altered). (Section 2, Measure 1.1)

> c) The icon or equivalent label may appear in different sizes depending on the context, as long as Signatories ensure that the disclosure is clear and distinguishable to natural persons. The icon or equivalent label may be expressed in different styles (e.g., contrast ratio, colour, or typography), as long as it remains clear, accessible, and distinguishable, i.e., readable and recognisable to natural persons. (Section 2, Measure 1.1)

> An EU icon following the design specifications for visual disclosure is publicly available for everyone to use freely (see Annex 1). (Section 2, Measure 1.1)

> Where visual disclosure is not possible (e.g., audio-only content), Signatories will implement the following design specifications:
>
> a) The disclosure will include, at the beginning of the deep fake itself, a short audible disclaimer in plain and simple natural language, either in the same language as the content or in English, disclosing the artificial origin of the audio deep fake in a perceivable manner.
>
> b) Where appropriate, the audio disclaimer will be complemented with information regarding whether it is AI-generated or manipulated. Signatories are furthermore encouraged to disclose what has been modified by the AI system. (Section 2, Measure 1.1)

> Alternatively, Signatories may develop and rely on other forms of audible disclosures (e.g., an earcon) ahead of the development of a common EU-wide audio solution by the Task Force, described in Measure 1.3, if the deployment of such an audible disclosure solution is accompanied by appropriate awareness raising measures (e.g., public information campaigns, repeated explanatory notices or disclaimers) to ensure broad understanding of the solution by the natural persons exposed to the deep fake audio. (Section 2, Measure 1.1)

> Signatories will ensure accessible disclosure with respect to different content modalities and contexts in accordance with applicable Union law, in particular Directive (EU) 2019/882 (the European Accessibility Act) and Directive (EU) 2016/2102 (the Web Accessibility Directive). This includes but is not limited to application of:
>
> a) audio descriptions or alternative cues for visual disclosure elements;
>
> b) tactile and haptic cues for audio-only content, considering the needs of end-users with hearing impediments (e.g., a vibration alert before audio playing identifying that the audio contains deep fake content);
>
> c) high contrast icons or equivalent labels and screen-reader compatibility, including for end-users with colour vision deficiencies;
>
> d) detectability of the icon or equivalent label by assistive technologies. (Section 2, Measure 1.1)

## Deployers: placement of the icon or label

> Signatories will apply the following overarching principles applicable to all content modalities and contexts, with the exception of deep fakes that are part of artistic, creative, satirical, fictional or analogous works that are subject to specific disclosure regime specified in Commitment 3:
>
> a) Considering the content format and dissemination context, the icon or equivalent label will be placed in an appropriate and perceivable manner that ensures immediate recognition by natural persons without requiring user (inter)action or sustained attention.
>
> b) The icon or equivalent label will remain visible at least for a sufficient duration to be noticed under normal exposure conditions to ensure perceivability.
>
> c) The icon or equivalent label will be directly embedded into the content, unless equivalent alternatives to an embedded icon are available (e.g., a user interface overlay that for natural persons appears to be on the content), as long as Signatories follow the placement specifications in this measure and, to their best effort aim to ensure disclosure of the deep fake or published text takes into account the distribution and dissemination chain of the content.
>
> d) The icon or equivalent label will be clearly perceivable and distinguishable at the latest at the time of first exposure of a natural person to the deep fake or published text (e.g., by maintaining sufficient spacing to other overlay elements, disclaimers, and sound/visual on-screen/on-display elements and remain visible against any background). (Section 2, Sub-measure 1.2.1)

> In addition to the overarching principles, Signatories will implement the following placement specifications where visual disclosure is possible:
>
> a) The icon or equivalent label will appear in an appropriate place where no intervening overlay elements exist (e.g., in the top right corner of an image or video deep fake).
>
> b) To account for situations where different natural persons may be exposed to deep fake video at different moments (e.g., live content) and to account for downstream use (e.g., screenshots and clipped fragments), Signatories will display the icon or equivalent label at the beginning of the video as well as, where possible, at regular intervals throughout the video and, at a minimum, after interruptions (e.g., after commercial or advertising breaks). Where possible and appropriate depending on the context, Signatories are furthermore encouraged to display the icon or equivalent label throughout the deep fake video or during the deep fake part of the video, where the deep fake segment does not necessarily span the entire duration of the video. (Section 2, Sub-measure 1.2.2)

> c) Where a deep fake is exclusively used as part of a closed internal professional context (e.g., for the purpose of training or informing employees), the disclosure may be placed in the user interface, physical setting or any other appropriate medium readily available to the natural persons exposed to the deep fake, informing them before being exposed to the deep fake, as long as it is clear and distinguishable for the natural persons involved in the professional setting. (Section 2, Sub-measure 1.2.2, point c)

> d) For visual deep fakes, audible disclosures may only be implemented as an additional disclosure method and will always be accompanied by visual disclosures (e.g., where audio is part of the user experience or as appropriate for accessibility purposes).
>
> e) For audio deep fakes, when a screen is available, an additional visual disclosure based on the icon or equivalent label will be made available (e.g., when a screen is available in a car or on a smartphone display), in addition to the audible disclaimer. (Section 2, Sub-measure 1.2.2, points d and e)

> f) For published text, Signatories will place the icon or equivalent label, for example above or at the top of the text, near the headline of the text, or in the colophon at the beginning of the text, as long as placement is clear, consistent, and distinguishable for the end-user. Where appropriate, Signatories may label only that part of the text which is AI-generated or manipulated. For short text (single words or brief phrases), where labelling the text outputs would degrade readability and usability, Signatories must still carry out the labelling but may ensure disclosure through a contextual notice in the user interface (e.g., an indicator adjacent to the output, or disclosing that AI is used in the beginning of a user exposure session or when first time interacting with the content). (Section 2, Sub-measure 1.2.2, point f)

> In addition to the overarching principles, where visual disclosure is not possible, Signatories will include an audible disclaimer at the latest at the time of the first exposure to the deep fake. Additionally, audible cues may be used (e.g., tones or earcons) to support recognition. (Section 2, Sub-measure 1.2.3)

> In order to cater for downstream use (e.g., clipped audio fragments) and for long-form or live exposure, Signatories will, where appropriate, supplement the initial audible disclaimer at the beginning of the content with reminders at regular intervals (e.g., disclaimers, tones or earcons) for the entire duration of the audio deep fake to ensure ongoing awareness, and at minimum after interruptions (e.g., by advertisements). (Section 2, Sub-measure 1.2.3)

## Deployers: artistic works and human review of published text

> In accordance with Article 50(4) AI Act, Signatories commit to implement measures to disclose deep fakes that form part of evidently artistic, creative, satirical, fictional or analogous work or programmes in a way that does not hamper the display or enjoyment of the work, including its normal exploitation and use, while maintaining the utility and quality of the work. (Section 2, Commitment 3)

> Where deep fake content is made available in a digital or interactive manner (e.g., on websites, apps or other user interfaces), the icon or equivalent label may be placed outside but adjacent to the video or image frame, or adjacent to the audio content and integrated into user interface elements or overlays, under the control of the Signatory. Signatories commit to ensure that any such contextual disclosure solution is perceivable by the end-user without the need to perform dedicated actions or additional engagement. Examples of contextual disclosure include disclosures as part of the user interface (e.g., as part of websites or application interfaces of smart glasses or other digital devices), short notes, a non-obtrusive icon or label that by clicking or hovering over provides more information, disclaimers appearing adjacent to the content. (Section 2, Commitment 3)

> All other Signatories, including those without such review or editorial procedures, commit to establish, adapt, or maintain appropriate policies for human review or editorial control prior to publication and that a natural or legal person holds editorial responsibility for the publication. These internal policies may rely on existing processes, will be proportionate to the deployer’s size and resources, and will include at least the following elements:
>
> a) The identification of the natural or legal person with editorial responsibility (name, role and contact details);
>
> b) An overview of the concrete organisational measures as well as human resources, allocated to ensure adequate human review or editorial control is performed and editorial responsibility is assumed before publication of the published text. This does not entail having to document individual instances of human review or editorial control over individual text publications. (Section 2, Commitment 4)

## The EU icon

> This Annex contains the EU icons that may be used by deployers to comply with Measure 1.1. Three main icons are provided. One icon is intended to disclose fully AI-generated deep fakes or published text (Figure 1), a second icon is intended to disclose AI-manipulated/partially modified deep fakes or published text (Figure 2), and a third basic icon is included to enable deployers to supplement it with an interactive layer with further information or an alternative textual label, where appropriate (Figure 3). (Annex 1)

> These icons are publicly available for Signatories to use in line with the placement specifications, without the need for attribution to the Commission or the AI Office. (Annex 1)
