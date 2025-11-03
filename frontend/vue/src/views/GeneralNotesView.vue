<template>
  <HeaderRow />
  <LogoAndSearchbarRow
    :placeholder="t('GeneralNotesView.searchplaceholder')"
    :showSearch="false"
    :showProgress="false"
  />
  <div class="main-container">
    <MenuBanner :menutext="t('GeneralNotesView.menutext')" :hint_before="true" :hinttext="t('GeneralNotesView.hint')" />
    <div v-if="$i18n.locale === 'en'" class="sub-container container">
      <div class="content-inner">
        <p>
          Terms and conditions of use of the THN HAnS platform within the framework of the HAnS research project
          Version: 1, Last change: 01.10.2024
        </p>
        <h2>1. General</h2>
        <p>
          The operator of the THN HAnS platform is the Technische Hochschule Nürnberg Georg Simon Ohm. The public area
          is subject to the terms of use of the TH Nürnberg website. The use of the public materials is limited by the
          licenses indicated with the materials. Any use beyond this (e.g. Media upload) is only available to registered
          users and is primarily aimed at lecturers and students of Technische Hochschule Nürnberg Georg Simon Ohm,
          hereinafter referred to as users. Users can log in to THN HAnS with their university account. The present
          terms and conditions of use must be accepted upon first login.
        </p>
        <h2>2. Term, amendment and termination of the Terms and Conditions of Use</h2>
        <p>
          These terms and conditions of use for the use of THN HAnS and the offers provided therein are initially valid
          for an indefinite period of time. However, they can be terminated by either party at any time, without giving
          reasons or compliance with deadlines by e-mail or in other written form. In the event of termination of the
          Terms of Use, the User will no longer be able to access his/her account on THN HAnS. The operator reserves the
          right to change these terms of use from time to time – also with effect for already existing user
          relationships – insofar as this appears necessary and the users are not unreasonably disadvantaged thereby. We
          will inform you of changes by posting a notice on THN HAnS. Users may then in any case terminate the User
          Agreement without giving reasons or complying with deadlines by e-mail or in other written form. This also
          applies if the right of termination is changed in the amended terms of use. If a user does not terminate the
          concluded user agreement after notification of the amended terms of use, or in particular continues to use THN
          HAnS after notification of the amended terms of use without termination, he / she accepts the amended terms of
          use communicated to him / her.
        </p>
        <h2>3. Registration</h2>
        <p>
          The users are responsible for the confidentiality of their own access data and inform the operator immediately
          in case of loss. The users are liable for any damages caused by the publication of their personal access data.
          The query of user data from the university directory service is agreed upon by logging in to THN HAnS.
        </p>
        <h2>4. Subject matter of the contract and service description</h2>
        <p>
          Users have the possibility to upload multimedia content such as videos, images, audios, documents &
          presentations. Anyone posting their own materials guarantees that he/she owns the rights to the materials and
          can dispose of them and that no exclusive rights have been granted to third parties so far. Anyone posting
          material also guarantees that it is in accordance with any copyrights of third parties. In both cases, the
          publisher must indicate all authors involved in the creation. The operator provides the users with their own
          profile. The users receive a simple right of use to use the services of THN HAnS. The user relationship is
          terminated when the account is removed from the university directory service. The offer is free of charge, but
          may only be used for university-related purposes, primarily in the context of teaching. In exceptional cases,
          other use is possible after consultation with the operator.
        </p>
        <h4>AI-based functionalities</h4>
        <p>
          The multimedia content is processed by AI models on servers of Technische Hochschule Nürnberg Georg Simon Ohm.
          The operator provides AI-based functionalities to users. The following describes the scope of performance and
          the purposes and restrictions of use of the AI-based functionalities.
        </p>
        <p><strong>Transcripts</strong></p>
        <p>
          The transcripts are created in the HAnS research project on the basis of video material, e.g. a lecture
          recorded on video, and generated automatically by means of a speech recognition tool. HAnS is a system that is
          currently under development. The underlying speech recognizer will be continuously improved during the course
          of the project. Therefore, there may be deviations in content from the spoken words. The transcripts do not
          claim to be a complete and correct reproduction of the oral lecture. For any purpose, including self-study
          and, if applicable, exam preparation, only the spoken word is valid.
        </p>
        <p><strong>Summaries</strong></p>
        <p>
          The summaries are automatically generated by a large language model (LLM) based on the transcripts as part of
          the HAnS research project. HAnS is a system that is currently under development. The underlying language model
          will be continuously improved during the course of the project. Therefore, there may be discrepancies in
          content due to the use of the large language model (LLM's) to the spoken words. The summaries do not claim to
          be a complete and accurate reproduction of the oral lecture or correct in content. For any purpose including
          self-study and, if applicable, exam preparation, only the spoken word applies.
        </p>
        <p><strong>Topics</strong></p>
        <p>
          Topics are automatically detected by a large language model (LLM) based on the transcripts and provided with
          short summaries in the HAnS research project. HAnS is a system that is currently under development. The
          underlying language model will be continuously improved during the course of the project. Therefore, there may
          be discrepancies in content due to the use of the large language model (LLM's) to the spoken words. The
          detected topics do not claim complete and correct playback times, topic names and correctness of content of
          the short summaries of the topics. For any purpose including self-study and, if applicable, exam preparation,
          only the spoken word applies.
        </p>
        <p><strong>Questions</strong></p>
        <p>
          The questions functionality within the HAnS research project uses a large language model (LLM) to generate
          multiple-choice questions and their solutions using the transcript of the video. The lecturers are able to
          create questions using the LLM or create manual questions before publishing the video to the students. These
          questions should be reviewed and approved by the lecturer and are displayed in 'Questions approved by
          lecturers on the respective topic'. If the lecturer did not review the LLM created content, the pre-generated
          questions for each video topic section are displayed in 'Automatically pre-generated questions on the
          respective topic'. The second option 'Dynamically generated questions by time interval' creates questions on
          the fly using transcript sections of the current video position at specific intervals. The default interval is
          3 minutes. With this setting a new multiple-choice question is generated by the LLM every 3 minutes while the
          video is being played. HAnS is a system that is currently under development. The underlying language model
          will be continuously improved during the course of the project. Therefore, there may be discrepancies in
          content and factually incorrect questions, answers and solutions due to the use of the large language model
          (LLM's). The questions, answers and solutions of the language model do not claim to be complete,
          non-discriminatory, or correct in content. Questions, answers and solutions may be freely invented through the
          use of the language model. For any purpose including self-study and possibly exam preparation, only the spoken
          word applies.
        </p>
        <p><strong>Chat</strong></p>
        <p>
          The chat functionality within the HAnS research project uses a large language model (LLM) or a vision large
          language model (VLLM) to generate responses. HAnS is a system that is currently under development. The
          underlying language model will be continuously improved during the course of the project. Therefore, there may
          be discrepancies in content and factually incorrect responses due to the use of the large language model
          (LLM's). The responses of the language model do not claim to be complete, non-discriminatory, or correct in
          content. Answers may be freely invented through the use of the language model. For any purpose including
          self-study and possibly exam preparation, only the spoken word applies.
        </p>
        <p><strong>Links</strong></p>
        <p>
          Links are automatically extracted by a vision large language model (VLLM) based on the slides text. HAnS is a
          system that is currently under development. The underlying language model will be continuously improved during
          the course of the project. Therefore, there may be deviations in the content of the links. The link list shown
          may not be correct and complete. For any purpose including self-study and, if applicable, exam preparation,
          only the links shown in the video and in the slides are valid.
        </p>
        <p><strong>Keywords</strong></p>
        <p>
          Keywords are automatically detected by a large language model (LLM) based on the extracted slides text from a
          vision large language model (VLLM). HAnS is a system that is currently under development. The underlying
          language model will be continuously improved during the course of the project. Therefore, there may be
          discrepancies in content due to the use of the large language model (LLM's) for the keywords. The detected
          keywords do not claim complete and correct. For any purpose including self-study and, if applicable, exam
          preparation, only the spoken word applies.
        </p>
        <h2>5. Legality of the contents</h2>
        <p>
          The users are solely responsible for the multimedia contents they upload to THN HAnS. Content uploaded to THN
          HAnS must not violate applicable laws and regulations, good morals and in particular the rights of third
          parties (name, personality, copyright, data protection rights, etc. ) verstoßen. Users may not upload content
          that violates the provisions of the Criminal Code, the Youth Media Protection State Treaty (JMStV) or the
          Narcotics Act, the Pharmaceutical Act or the Weapons Act. No pornographic, violent, racist or hateful content
          may be used on THN HAnS. It may not call for criminal offences or present instructions for this. No content or
          comments may be displayed on THN HAnS that insult, defame, harass or otherwise harm other users. Users may not
          use data that by its nature or nature, size or reproduction (e.g. B. Spamming) are likely to endanger the
          existence or operation of THN HAnS. The use of computer programs for the automatic reading of data, e.g. B.
          Crawler, is not permitted without the express consent of the operator of TH HAnS. The operator is entitled to
          refuse the inclusion of content, to delete and block content immediately and to remove the pages and
          references to them immediately.
        </p>
        <h2>6. Availability of the contents</h2>
        <p>
          There is no guarantee or warranty for the availability of THN HAnS and its services. The operator offers no
          warranty for such defects that are not within its sphere of influence, for example force majeure, the fault of
          third parties or that arise from external influences, operating errors, not carried out changes, additions,
          installations or extensions, repair attempts or other manipulations. Access to the services may be restricted
          if the security of the network operation, the maintenance of the network integrity, in particular the
          prevention of serious disruptions of the network, the software or stored data require this. Contact for error
          messages or problem cases is the collaborative project HAnS of Technische Hochschule Nürnberg Georg Simon Ohm,
          which can be reached via the email address
          <a href="mailto:verbundprojekt-hans@th-nuernberg.de"
            >verbundprojekt-hans<span class="fa fa-at"><span data-v-76732dca="" class="sr-only">at</span></span
            >th-nuernberg<span class="fa fa-circle dot-subst"><span class="sr-only">Punkt</span></span
            >de</a
          >.
        </p>
        <h2>7. Liability for contents on THN HAnS</h2>
        <p>
          The operator of THN HAnS is only liable for damages that are based on intentional or grossly negligent
          breaches of contract on his part. Excluded are claims for damages on the basis of life, body and health. The
          objection of the user’s co-culpability remains unaffected by the operator of THN HAnS. The operator is not
          liable for the content posted by users. Users are solely responsible for ensuring that they have the necessary
          rights to use the multimedia content. The operator has the following obligations: upon becoming aware of the
          illegality of certain uploaded contents, actions must be taken to prevent access to these contents or to
          remove them from THN HAnS.
        </p>
        <h2>8. Applicable law</h2>
        <p>
          These terms and conditions of use and the entire legal relationship between the users and the operator are
          subject to the laws of the Federal Republic of Germany.
        </p>
        <h2>9. Place of jurisdiction</h2>
        <p>The place of jurisdiction for all disputes arising in connection with the THN HAnS portal is Nürnberg.</p>
      </div>
    </div>
    <div v-else class="container">
      <div class="content-inner">
        <p>
          Nutzungsbedingungen der Plattform THN HAnS im Rahmen des Forschungsprojektes HAnS Version: 1, Letzte Änderung:
          01.10.2024
        </p>
        <h2>1. Allgemeines</h2>
        <p>
          Der Betreiber der Plattform THN HAnS ist die Technische Hochschule Nürnberg Georg Simon Ohm. Der öffentliche
          Bereich unterliegt den Nutzungsbedingungen der Webseite der TH Nürnberg. Die Nutzung der öffentlichen
          Materialien ist durch die bei den Materialien angegebenen Nutzungslizenzen beschränkt. Eine darüber hinaus
          gehende Nutzung (z.B. Medienupload) ist nur für registrierte Personen möglich und richtet sich vorrangig an
          Lehrende der TH Nürnberg, im Folgenden als Nutzer bezeichnet. Nutzer können sich mit ihrem Hochschul-Account
          auf THN HAnS einloggen. Beim erstmaligen Login müssen die vorliegenden Nutzungsbedingungen akzeptiert werden.
        </p>
        <h2>2. Laufzeit, Änderung und Kündigung der Nutzungsbedingungen</h2>
        <p>
          Diese Nutzungsbedingungen über die Verwendung von THN HAnS und der dort bereitgestellten Angebote gelten
          zunächst für unbestimmte Zeit. Sie können jedoch von beiden Seiten jederzeit, ohne Angabe von Gründen oder
          Einhaltung von Fristen per E-Mail oder in anderer Schriftform gekündigt werden. Im Falle einer Kündigung der
          Nutzungsbedingungen kann der Nutzer nicht mehr auf seinen Account auf THN HAnS zugreifen. Der Betreiber behält
          sich vor, diese Nutzungsbedingungen von Zeit zu Zeit – auch mit Wirkung für bereits bestehende
          Nutzungsverhältnisse – zu ändern, soweit dies notwendig erscheint und die Nutzer hierdurch nicht unangemessen
          benachteiligt werden. Änderungen teilen wir über einen Hinweis auf THN HAnS mit. Nutzer können daraufhin in
          jedem Fall die Nutzungsvereinbarung ohne Angabe von Gründen oder Einhaltung von Fristen per E-Mail oder in
          anderer Schriftform kündigen. Dies gilt auch, wenn das Kündigungsrecht in den geänderten Nutzungsbedingungen
          abgeändert werden sollte. Kündigt ein Nutzer nicht nach Mitteilung der geänderten Nutzungsbedingungen die
          abgeschlossene Nutzungsvereinbarung, oder setzt insbesondere die Nutzung von THN HAnS nach Mitteilung der
          geänderten Nutzungsbedingungen ohne Ausspruch einer Kündigung fort, akzeptiert er/ sie damit die geänderten
          und ihm/ ihr mitgeteilten Nutzungsbedingungen.
        </p>
        <h2>3. Registrierung</h2>
        <p>
          Die Nutzer sorgen selbst für die Geheimhaltung der eigenen Zugangsdaten und informieren den Betreiber
          unverzüglich bei Verlust. Die Nutzer haften selbst für Schäden, die durch eine Veröffentlichung der
          persönlichen Zugangsdaten entstehen. Der Abfrage von Nutzerdaten aus dem Verzeichnisdienst der Hochschule wird
          mit dem Login auf THN HAnS zugestimmt.
        </p>
        <h2>4. Vertragsgegenstand und Leistungsbeschreibung</h2>
        <p>
          Die Nutzer haben die Möglichkeit multimediale Inhalte, wie Videos, Bilder, Audios, Dokumente & Präsentationen
          hochzuladen. Wer eigene Materialien einstellt, versichert, dass er/sie die Rechte an den Materialien innehat
          und darüber verfügen kann und dass Dritten bislang keine ausschließlichen Rechte eingeräumt worden sind. Wer
          Material einstellt, versichert entsprechend auch, dass dies im Einklang mit eventuellen Urheberrechten Dritter
          steht. In beiden Fällen hat die/der Einstellende alle an der Erstellung beteiligten Urheber und Urheberinnen
          anzugeben. Der Betreiber stellt den Nutzern ein eigenes Profil zur Verfügung. Die Nutzer erhalten ein
          einfaches Nutzungsrecht, die Dienstleistungen von THN HAnS zu nutzen. Die Beendigung des Nutzerverhältnisses
          erfolgt mit dem Ausscheiden des Accounts aus dem Verzeichnisdienst der Hochschule. Das Angebot ist kostenfrei,
          darf aber nur für hochschulbezogene Zwecke, vorrangig im Rahmen der Lehre, verwendet werden. In Ausnahmefällen
          ist eine andersartige Nutzung nach Absprache mit dem Betreiber möglich.
        </p>
        <h4>KI-basierte Funktionalitäten</h4>
        <p>
          Die multimedialen Inhalte werden durch KI-Modelle auf Servern der Technische Hochschule Nürnberg Georg Simon
          Ohm verarbeitet. Der Betreiber stellt den Nutzern KI-basierte Funktionalitäten bereit. Im Folgenden werden der
          Leistungsumfang und die Verwendungszwecke der KI-basierten Funktionalitäten beschrieben.
        </p>
        <p><strong>Transkripte</strong></p>
        <p>
          Die Transkripte werden im Rahmen des Forschungsprojektes HAnS auf Basis von Videomaterial, z. B. einer auf
          Video aufgenommenen Vorlesung, erstellt und mittels eines Spracherkennungstools automatisch generiert. Es
          handelt sich bei HAnS um ein System, das sich in der Entwicklung befindet. Der zugrunde liegende
          Spracherkenner wird im Laufe des Projektes laufend verbessert. Es kann daher zu inhaltlichen Abweichungen zum
          gesprochenen Wort kommen. Die Transkripte erheben keinen Anspruch auf vollständige und richtige Wiedergabe der
          mündlichen Vorlesung. Für jedwede Zwecke einschließlich Selbststudium und ggf. Prüfungsvorbereitung gilt
          ausschließlich das gesprochene Wort.
        </p>
        <p><strong>Zusammenfassungen</strong></p>
        <p>
          Die Zusammenfassungen werden im Rahmen des Forschungsprojektes HAnS auf Basis der Transkripte automatisch
          durch ein großes Sprachmodell (LLM) generiert. Es handelt sich bei HAnS um ein System, das sich in der
          Entwicklung befindet. Das zugrunde liegende Sprachmodell wird im Laufe des Projektes laufend verbessert. Es
          kann daher zu inhaltlichen Abweichungen durch die Nutzung des großen Sprachmodells (LLM's) zum gesprochenen
          Wort kommen. Die Zusammenfassungen erheben keinen Anspruch auf vollständige und richtige Wiedergabe der
          mündlichen Vorlesung und inhaltliche Korrektheit. Für jedwede Zwecke einschließlich Selbststudium und ggf.
          Prüfungsvorbereitung gilt ausschließlich das gesprochene Wort.
        </p>
        <p><strong>Themen</strong></p>
        <p>
          Die Themen werden im Rahmen des Forschungsprojektes HAnS auf Basis der Transkripte automatisch durch ein
          großes Sprachmodell (LLM) erkannt und mit kurzen Zusammenfassungen versehen. Es handelt sich bei HAnS um ein
          System, das sich in der Entwicklung befindet. Das zugrunde liegende Sprachmodell wird im Laufe des Projektes
          laufend verbessert. Es kann daher zu inhaltlichen Abweichungen durch die Nutzung des großen Sprachmodells
          (LLM's) zum gesprochenen Wort kommen. Die erfassten Themen erheben keinen Anspruch auf vollständige und
          richtige Wiedergabezeitpunkte, Themennamen und inhaltliche Korrektheit der kurzen Zusammenfassungen der
          Themen. Für jedwede Zwecke einschließlich Selbststudium und ggf. Prüfungsvorbereitung gilt ausschließlich das
          gesprochene Wort.
        </p>
        <p><strong>Fragen</strong></p>
        <p>
          Die Fragen-Funktionalität im Rahmen des Forschungsprojektes HAnS verwendet ein großes Sprachmodell (LLM) um
          Multiple-Choice-Fragen und deren Lösung mit Hilfe des Transkripts des aktuellen Videos. Die Dozenten können
          manuelle Fragen oder Fragen mit dem LLM erstellen, bevor sie das Video für die Studenten veröffentlichen.
          Diese Fragen werden vom Dozenten geprüft und freigegeben und sind im Reiter 'Durch Dozierende freigegebene
          Fragen zum jeweiligen Thema' zu finden. Wenn der Dozent den vom LLM erstellten Inhalt nicht überprüft hat,
          werden vorab generierte Fragen für jeden Video-Themenbereich in 'Automatisch vorab generierte Fragen zum
          jeweiligen Thema' angezeigt. Die zweite Option 'Dynamisch generierte Fragen nach Zeitintervall' erstellt
          Fragen während der Wiedergabe und verwendet Abschnitte aus dem Transkript mit Bezug zur aktuellen
          Videoposition in eingestellten Intervallen. Der eingestellte Standardintervall beträgt 3 Minuten. Mit dieser
          Einstellung wird alle 3 Minuten eine neue Multiple-Choice-Frage vom LLM generiert, während das Video
          abgespielt wird. Es handelt sich bei HAnS um ein System, das sich in der Entwicklung befindet. Das zugrunde
          liegende Sprachmodell wird im Laufe des Projektes laufend verbessert. Es kann daher zu inhaltlichen
          Abweichungen und faktisch nicht korrekten Fragen, Antworten und Lösungen durch die Nutzung des großen
          Sprachmodells (LLM's) kommen. Die Fragen, Antworten und Lösungen des Sprachmodells erheben keinen Anspruch auf
          Vollständigigkeit, Diskriminierungsfreiheit und inhaltliche Korrektheit. Fragen, Antworten und Lösungen können
          durch das verwendete Sprachmodell frei erfunden werden. Für jedwede Zwecke einschließlich Selbststudium und
          ggf. Prüfungsvorbereitung gilt ausschließlich das gesprochene Wort.
        </p>
        <p><strong>Chat</strong></p>
        <p>
          Die Chat-Funktionalität im Rahmen des Forschungsprojektes HAnS verwendet ein großes Sprachmodell (LLM) oder
          ein großes Bild-Sprachmodell (VLLM) um Antworten zu erzeugen. Es handelt sich bei HAnS um ein System, das sich
          in der Entwicklung befindet. Das zugrunde liegende Sprachmodell wird im Laufe des Projektes laufend
          verbessert. Es kann daher zu inhaltlichen Abweichungen und faktisch nicht korrekten Antworten durch die
          Nutzung des großen Sprachmodells (LLM's) kommen. Die Antworten des Sprachmodells erheben keinen Anspruch auf
          Vollständigigkeit, Diskriminierungsfreiheit und inhaltliche Korrektheit. Antworten können durch das verwendete
          Sprachmodell frei erfunden werden. Für jedwede Zwecke einschließlich Selbststudium und ggf.
          Prüfungsvorbereitung gilt ausschließlich das gesprochene Wort.
        </p>
        <p><strong>Links</strong></p>
        <p>
          Links werden automatisch von einem großen Bild-Sprachmodell (VLLM) basierend auf dem Folientext extrahiert.
          HAnS ist ein System, das sich derzeit in der Entwicklung befindet. Das zugrunde liegende Sprachmodell wird im
          Laufe des Projektes laufend verbessert. Es kann daher bei der Auflistung der Links zu inhaltlichen
          Abweichungen kommen. Die gezeigte Linkliste ist möglicherweise nicht korrekt und vollständig. Für jegliche
          Zwecke, einschließlich Selbststudium und ggf. Prüfungsvorbereitung, gelten nur die gezeigten Links im Video
          und in den Folien.
        </p>
        <p><strong>Schlagworte</strong></p>
        <p>
          Die Schlagworterkennung erfolgt automatisch über ein großes Sprachmodell (LLM) auf Basis des extrahierten
          Folientextes aus einem großen Bild-Sprachmodell (VLLM). HAnS ist ein System, das sich derzeit in der
          Entwicklung befindet. Das zugrunde liegende Sprachmodell wird im Laufe des Projektes laufend verbessert. Daher
          kann es aufgrund der Verwendung der großen Sprachmodelle (LLM's) für die Schlagworte zu inhaltlichen
          Abweichungen kommen. Die erkannten Schlagworte sind möglicherweise nicht korrekt und vollständig. Für jedwede
          Zwecke einschließlich Selbststudium und ggf. Prüfungsvorbereitung gilt ausschließlich das gesprochene Wort.
        </p>
        <h2>5. Rechtmäßigkeit der Inhalte</h2>
        <p>
          Die Nutzer allein sind für die durch sie auf THN HAnS eingestellten multimedialen Inhalte selbst
          verantwortlich. Auf THN HAnS hochgeladene Inhalte dürfen nicht gegen geltendes Gesetz und Rechtsvorschriften,
          die guten Sitten und insbesondere gegen die Rechte Dritter (Namens-, Persönlichkeits-, Urheber-,
          Datenschutzrechte usw.) verstoßen. Die Nutzer dürfen keine Inhalte hochladen, die gegen Bestimmungen des
          Strafgesetzbuches, Jugendmedienschutz-Staatsvertrag (JMStV) oder gegen das Betäubungsmittelgesetz,
          Arzneimittelgesetz oder Waffengesetz verstoßen. Es dürfen keine pornografischen, gewaltverherrlichenden,
          rassistischen oder volksverhetzenden Inhalte auf THN HAnS verwendet werden. Es darf nicht zu Straftaten
          aufgerufen oder Anleitungen hierfür dargestellt werden. Es dürfen keine Inhalte oder Kommentare auf THN HAnS
          dargestellt werden, die andere Nutzer beleidigen, verleumden, belästigen oder in sonstiger Weise schädigen.
          Die Nutzer dürfen keine Daten verwenden, die nach ihrer Art oder Beschaffenheit, Größe oder Vervielfältigung
          (z.B. Spamming) geeignet sind, den Bestand oder Betrieb von THN HAnS zu gefährden. Der Einsatz von
          Computerprogrammen zum automatischen Auslesen von Daten, wie z.B. Crawler, ist ohne ausdrückliche Zustimmung
          des Betreibers von TH HAnS nicht gestattet. Der Betreiber ist berechtigt, die Aufnahme von Inhalten zu
          verweigern, Inhalte unverzüglich zu löschen und zu sperren sowie die Seiten und darauf gerichtete Verweise
          sofort zu entfernen.
        </p>
        <h2>6. Verfügbarkeit der Inhalte</h2>
        <p>
          Es gibt keine Garantie oder Gewährleistung für die Verfügbarkeit von THN HAnS und seiner Dienstleistungen. Der
          Betreiber bietet keine Gewährleistung für solche Mängel, die nicht in seinem Einflussbereich liegen, zum
          Beispiel höhere Gewalt, Verschulden Dritter oder die durch äußere Einflüsse, Bedienungsfehler, nicht
          durchgeführte Änderungen, Ergänzungen, Ein- oder Ausbauten, Reparaturversuche oder sonstige Manipulationen
          entstehen. Der Zugang zu den Dienstleistungen kann beschränkt werden, sofern die Sicherheit des Netzbetriebes,
          die Aufrechterhaltung der Netzintegrität, insbesondere die Vermeidung schwerwiegender Störungen des Netzes,
          der Software oder gespeicherter Daten dies erfordern. Kontakt bei Fehlermeldungen oder Problemfällen ist das
          Verbundprojekt HAnS der Technischen Hochschule Nürnberg Georg Simon Ohm, das über die Emailadresse
          <a href="mailto:verbundprojekt-hans@th-nuernberg.de"
            >verbundprojekt-hans<span class="fa fa-at"><span data-v-76732dca="" class="sr-only">at</span></span
            >th-nuernberg<span class="fa fa-circle dot-subst"><span class="sr-only">Punkt</span></span
            >de</a
          >
          erreicht werden kann.
        </p>
        <h2>7. Haftung für Inhalte auf THN HAnS</h2>
        <p>
          Der Betreiber von THN HAnS haftet nur für Schäden, die auf vorsätzlichen oder grob fahrlässigen
          Vertragsverletzungen seinerseits beruhen. Ausgenommen sind Schadensersatzansprüche auf Grund des Lebens, des
          Körpers und der Gesundheit. Der Einwand des Mitverschuldens der Nutzer bleibt dem Betreiber von THN HAnS
          unbenommen. Der Betreiber haftet nicht für die durch Nutzer eingestellten Inhalte. Die Nutzer allein haben
          dafür Sorge zu tragen, dass sie die erforderlichen Nutzungsrechte an den multimedialen Inhalten besitzen. Der
          Betreiber hat folgende Prüfungspflichten: bei Kenntniserlangung von der Rechtswidrigkeit bestimmter
          hochgeladener Inhalte sind Handlungen zu unternehmen, den Zugang zu diesen Inhalten zu unterbinden oder diese
          von THN HAnS zu entfernen.
        </p>
        <h2>8. Geltendes Recht</h2>
        <p>
          Für diese Nutzungsbedingungen und die gesamten Rechtsbeziehungen zwischen den Nutzern und dem Betreiber gilt
          das Recht der Bundesrepublik Deutschland.
        </p>
        <h2>9. Gerichtsstand</h2>
        <p>Gerichtsstand für alle im Zusammenhang mit dem Portal THN HAnS entstehenden Streitigkeiten ist Nürnberg.</p>
      </div>
    </div>
  </div>
  <BottomRow />
</template>
<script setup lang="ts">
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";
import MenuBanner from "@/components/MenuBanner.vue";
import {useI18n} from "vue-i18n";
import {matomo_trackpageview, matomo_clicktracking} from "@/common/matomo_utils";
import {useAuthStore} from "@/stores/auth";

const {t} = useI18n({useScope: "global"});

const authStore = useAuthStore();
const authRole = authStore.getRole();
const chatEnabled =
  authRole !== undefined && (authRole === "admin" || authRole === "developer" || authRole === "lecturer");

matomo_trackpageview();
</script>

<style scoped>
.container {
  /* Removes redundant padding and margin from the bootstrap container class */
  padding: 0;
  margin: 0;
}
</style>
