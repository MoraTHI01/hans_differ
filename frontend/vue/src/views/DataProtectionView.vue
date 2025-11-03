<template>
  <HeaderRow />
  <LogoAndSearchbarRow
    :placeholder="t('DataProtectionView.searchplaceholder')"
    :showSearch="false"
    :showProgress="false"
  />
  <div class="main-container">
    <MenuBanner :menutext="t('DataProtectionView.menutext')" />
    <div class="row sub-container">
      <div class="col-md-9 col-md-offset-3">
        <div v-if="$i18n.locale === 'en'" class="col-content">
          <section class="content content-text">
            <div class="container">
              <div class="content-inner">
                <h2>Privacy Policy</h2>
                <p><strong>This is the Privacy Policy of:</strong></p>
                <p>
                  Technische Hochschule Nürnberg Georg Simon Ohm<br />Kesslerplatz 12<br />90489 Nuremberg<br />-
                  hereinafter referred to as Nuremberg Tech -
                </p>
                <p>
                  Nuremberg Tech takes data protection seriously. All of its data collection is carried out in
                  accordance with the statutory regulations. Further detailed information about these can be found at
                  <a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="https://www.datenschutz.de/"
                    title="Opens internal link in current window"
                    target="_blank"
                    class="external-link-new-window"
                    >www.datenschutz.de</a
                  >.
                </p>
                <p>
                  Nuremberg Tech’s data protection officer, Michael Günther, can be reached at
                  <a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="mailto:datenschutz@th-nuernberg.de"
                    title="Opens internal link in current window"
                    class="mail"
                    >datenschutz<span class="fa fa-at"><span class="sr-only">at</span></span
                    >th-nuernberg<span class="fa fa-circle dot-subst"><span class="sr-only">Punkt</span></span
                    >de</a
                  >
                </p>
              </div>
            </div>
          </section>
          <div>
            <h2>Data Protection Officer</h2>
            <div class="tx-persons">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th></th>
                    <th>Name</th>
                    <th>Contact</th>
                  </tr>
                </thead>
                <tbody>
                  <tr itemscope="" itemtype="http://schema.org/Person">
                    <td style="width: 58px; padding-left: 0">
                      <img
                        class="img-responsive"
                        alt="Michael Günther"
                        src="/bootstrap-icons/person.svg"
                        width="50"
                        height="70"
                      />
                    </td>
                    <td>
                      <strong class="text-primary">
                        <a
                          @click="matomo_clicktracking('click_link', $event.target.href)"
                          href="/en/person/guenther-michael/"
                        >
                          <span itemprop="givenName">Michael</span> <span itemprop="familyName">Günther</span>
                          <i class="fa fa-angle-right"></i>
                        </a>
                      </strong>

                      <br />M.A., Dipl.-Bibl. (FH)
                    </td>
                    <td>
                      <ul class="fa-ul">
                        <li>
                          <i class="fa fa-li fa-phone"></i>
                          <span class="sr-only">telefon</span>
                          <span itemprop="telephone">+49 (0)911 5880 - 4200</span>
                        </li>
                        <li>
                          <i class="fa fa-li fa-envelope"></i>
                          <span class="sr-only">email</span>
                          <a
                            @click="matomo_clicktracking('click_link', $event.target.href)"
                            href="mailto:michael.guenther@th-nuernberg.de"
                            >michael.guenther<span class="fa fa-at"><span class="sr-only">at</span></span
                            >th-nuernberg<span class="fa fa-circle dot-subst"><span class="sr-only">Punkt</span></span
                            >de</a
                          >
                        </li>
                        <li>
                          <i class="fa fa-li fa-fax"></i>
                          <span class="sr-only">fax</span>
                          <span itemprop="faxNumber">+49 (0)911 5880 - 8200</span>
                        </li>
                      </ul>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <section class="content content-text">
            <div class="container">
              <div class="content-inner">
                <p><strong>The following shall apply in principle:</strong></p>
                <p>
                  In order to ensure the appropriate security of your data during transfer, we use encryption processes
                  (e.g. SSL/TLS) and secured technical systems based on the state of the art.
                </p>
                <p>
                  Javascript is used as the active component for webpages. If you have disabled this function in your
                  browser, you will see the relevant prompt to re-activate it. When a user accesses a Nuremberg Tech
                  webpage and when they retrieve a file, this process may store data in a protocol file. The following
                  data set is then stored in each case:
                </p>
                <ul>
                  <li>Name of the retrieved file</li>
                  <li>Date and time of retrieval</li>
                  <li>Transferred data quantity</li>
                  <li>Report of whether retrieval was successful</li>
                  <li>Description of the type of web browser used</li>
                  <li>Requesting domain</li>
                </ul>
                <p>These raw statistical data are deleted once the process prompted by the user is complete.</p>
                <p>
                  It may be necessary for Nuremberg Tech’s servers to place cookies to enable the use of Nuremberg
                  Tech’s webpages. Two types of cookies are used.
                </p>
                <ul>
                  <li>
                    Session cookies are required partly for navigation on the portals of Nuremberg Tech. Session cookies
                    become invalid when the browser is closed or when there has been no activity on Nuremberg Tech’s
                    webpages for a certain period of time. When using a personalised area of the Nuremberg Tech portal,
                    the user is required to log in again.
                  </li>
                  <li>
                    Cookies for the provision of various services have a defined validity period that depends on the
                    special application in each case.
                  </li>
                </ul>
                <p>
                  <strong>Time limits for data deletion:</strong> Specific retention requirements and periods apply by
                  virtue of the statutory provisions. Once these periods have elapsed, the relevant data are routinely
                  deleted. For the rest, personal data are deleted as soon as they are no longer required for the
                  purpose for which they were collected or the legitimate basis for data handling ceases to apply (e.g.
                  as a result of withdrawal of consent). When an employee leaves the University’s employment, all
                  entries associated with this individual shall be deleted from the personal database within a
                  reasonable time, while on the other hand, all other editorial entries on university webpages will not
                  be deleted until the individual withdraws consent. In principle, individuals shall each be responsible
                  for deleting their own personal entries and links to internet search engines of other data
                  controllers.
                </p>
                <p>
                  <strong>Use analysis using Matomo: </strong>Nuremberg Tech uses the open-source software Matomo for
                  performing statistical analyses relating to this website. Information obtained in this manner shall
                  only be processed and analysed internally within Nuremberg Tech.
                </p>
                <p>
                  Recorded data shall not be forwarded to third parties. These serve the purpose of identifying and
                  improving relevant website content. IP addresses relating to these analyses are anonymized immediately
                  after processing and before they are stored.
                </p>
                <p>
                  Matomo, formerly known as Piwik, has been configured according to the recommendations of the
                  Independent State Data Protection Centre of Schleswig-Holstein (ULD) and complies with the applicable
                  data protection stipulations.
                </p>
                <p>
                  By using this website, you declare that you agree to the processing of data collected about you in the
                  aforementioned manner only for the purpose stated above. You can disable website use analysis by
                  Matomo by unticking the box shown below.
                </p>
                <p>
                  You can decide here whether to allow a unique web analysis cookie to be stored in your browser, which
                  will enable the website operator to record and analyse various statistical data.
                </p>
                <p>
                  Should you wish to decline it, please click decline on the consent screen in order to store the Matomo
                  deactivation cookie in your browser.
                </p>
              </div>
            </div>
          </section>
          <section class="content content-text">
            <div class="container">
              <div class="content-inner">
                <p>
                  The collected data will be used to optimize navigation on and content of the webpages of Nuremberg
                  Tech. Data will be analysed in their entirety, which means that analysis will not be expressly
                  performed on individual data attributable to users. The collected data will not be forwarded to
                  external parties.
                </p>
                <p>
                  The data created as part of user registration will be analysed in anonymized form for the purpose of
                  analysis by Nuremberg Tech. Addresses will not be sold to third parties.
                </p>
                <p>
                  Users who register on the Nuremberg Tech portal will cease to be anonymous. Whenever they log onto our
                  website, users are able to use Nuremberg Tech’s services according to the selected service and their
                  user authorisation. When a registered user contacts Nuremberg Tech IT support, a ticket is created for
                  the incident. This ticket is stored in order to create an advice history should a client send repeated
                  queries, for the purpose of ensuring rapid handling for the client.
                </p>
                <p>
                  If email addresses are used that are provided by Nuremberg Tech, all incoming emails are scanned using
                  various automated procedures:
                </p>
                <ul>
                  <li>
                    <em>Greylisting:</em> Nuremberg Tech uses greylisting as an anti-spam measure. This means that
                    emails sent to university email addresses are initially rejected. The server from which the email
                    was sent is requested to “try again later”. RFC-compliant servers do this and send the email again
                    after a short time, upon which the email is accepted and delivered. The email sender will notice
                    nothing apart from a delay in the delivery of the email. Servers that are not RFC-compliant (often
                    spammers) are usually unable to perform this repeated delivery.
                  </li>
                  <li>
                    <em>Virus scanners: </em>If an email is found to contain a virus, the email is deleted immediately
                    for security reasons. The recipient receives an automated email notification of this. The virus
                    scanner cannot be deactivated. Use of the virus scanner does not provide 100% security, but forms
                    part of the user’s personal security policy.
                  </li>
                  <li>
                    <em>Spam filter: </em>All incoming emails are scanned by the system for particular terms or word
                    combinations. The result of the scan is entered in an additional header field in the email. Emails
                    can then be automatically forwarded to a special email folder in the allocated inbox on the basis of
                    the header field. Emails that have been forwarded to the special folder can be automatically
                    deleted. Each user is able to configure this spam filter function themselves according to the
                    functions provided. The user is able to disable the spam filter at any time. Emails that have been
                    filtered or deleted can no longer be automatically forwarded to the inbox or restored.
                  </li>
                </ul>
                <p>
                  Nuremberg Tech makes some hosting capacity available within the scope of its services. Use of these
                  systems is subject to the General Terms and Conditions of Business of Nuremberg Tech.
                </p>
                <p>
                  Employees of Nuremberg Tech are required to observe confidentiality with regard to personal data.
                  These data will only be forwarded to third parties if this is required for the purpose of compliance
                  with official duties. These third parties are also required to comply with personal data protection
                  provisions.
                </p>
                <p>
                  All data available under “*.th-nuernberg.de” that are located on our servers and are hosted (stored)
                  there are protected against unauthorised access by security systems. The efficacy of protection is
                  tested by employees of Nuremberg Tech and its system service providers.
                </p>
                <p>
                  After a user leaves a page (such as by clicking on our banner advertisements), the selected target
                  site may place cookies. Nuremberg Tech has no legal responsibility for these cookies. For information
                  regarding the use of such cookies and the information stored in them by our advertising partners,
                  please check their privacy policies.
                </p>
                <p>
                  Nuremberg Tech draws attention to the fact that secured channels (VPNs) should always be used when
                  accessing the personalised area of the portal. This is the only way to ensure that personal data
                  transferred over the internet between users and Nuremberg Tech’s servers cannot be viewed by third
                  parties.
                </p>
                <p>
                  All operated servers on which personal data are processed or recorded for Nuremberg Tech users are
                  located within the Federal Republic of Germany.
                </p>
                <p>
                  The browser security settings make it possible to allow or prohibit the storing of cookies. Further
                  information about the use of cookies can also be found online on the website of the German Federal
                  Office for Information Security (<a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="http://www.bsi.de"
                    title="Opens internal link in current window"
                    target="_blank"
                    class="external-link-new-window"
                    >www.bsi.de</a
                  >).<br />If Nuremberg Tech instructs partner companies to perform particular services, the data
                  protection provisions shall be incorporated in the contracts and the partners shall be required to
                  comply with data protection law.
                </p>
                <p>
                  <strong>Contacting Nuremberg Tech using contact forms </strong>in relation to events and/or programmes
                  at Nuremberg Tech and to correct errors on webpages of Nuremberg Tech: our contact forms can be used
                  to send us a query or notification. To enable us to respond to you, it is necessary for you to provide
                  your name and email address. Further personal data may be provided to us voluntarily depending on the
                  form. The data will not be used for any other purpose or forwarded to third parties.
                </p>
                <h4>Events, press relations and public relations</h4>
                <p>
                  Nuremberg Tech also acts as a (co-) organiser of various events.<br />In the case of an invitation to
                  or participation in an event, Nuremberg Tech will process personal data (name, address, etc.). This
                  may take place via various communication channels, such as by completing a (web) form or by email or
                  telephone.
                </p>
                <p>
                  The personal data provided to Nuremberg Tech for this purpose are indicated in the relevant (web) form
                  or by the data requested during a call.
                </p>
                <h5>Data collected from accompanying persons</h5>
                <p>
                  For the purpose of proper running of the event, data from persons accompanying invited participants
                  are also collected and processed. These persons shall have the same rights as stated here for all
                  other persons affected by data collection, including rights to information regarding the nature and
                  quantity of data, making objections to processing, and deletion of data in particular. Attention is
                  drawn in this regard to the explanations under Right to information and Rectifications below.
                </p>
                <h5>Further processing of collected data</h5>
                <p>
                  Personal data will not be forwarded to third parties without authorisation, but shall be stored and
                  processed for internal use within Nuremberg Tech and for the purpose of organising and running events
                  (such as compiling guest lists, enabling entry checks, etc.) Nuremberg Tech may arrange for data to be
                  forwarded to one or more contractual processors that use(s) personal data at the instruction of
                  Nuremberg Tech and only for internal use that is attributable to Nuremberg Tech.
                </p>
                <p>
                  Depending on the nature of the event, Nuremberg Tech shall act as a co-organiser alongside an
                  additional cooperation partner. In such cases, the data collected for the purpose of the event will be
                  forwarded to our cooperation partners, who will also be permitted to use these data exclusively for
                  ensuring the proper running of the event. Notification regarding exactly which cooperation partners
                  are involved in an individual case shall be provided separately within the scope of organising the
                  event.
                </p>
                <p>
                  Data shall be stored only for as long as necessary for the organisation and running of events, and in
                  order to perform our duties relating to public relations.
                </p>
                <p>
                  As a recipient of correspondence/invitations, you may object to receiving any further
                  correspondence/invitations at any time.
                </p>
                <h5>Video/audio recording and photography</h5>
                <p>
                  Within the scope of performing Nuremberg Tech’s press and public relations duties, video/audio
                  recordings and photographs may be taken and used, in/on which you may be identifiably featured. The
                  produced audio/visual material may be used free of any fee and without restriction in terms of time,
                  space or content. You are also entitled to object to this. Please use the contact details shown to
                  file your objection.
                </p>
                <h4>Privacy notice in relation to social media</h4>
                <p>
                  Clicking on the social media buttons on the Nuremberg Tech website will take the user to Nuremberg
                  Tech’s pages on the social media sites. The user therefore leaves the Nuremberg Tech website. All
                  users must independently protect their personal data when using social networking sites. Users must
                  take note of the data protection provisions on these sites and manage their personal settings.
                </p>
                <p>And additionally in so far as we process personal data under our own responsibility for:</p>
                <ul>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://twitter.com/TH_Nuernberg"
                      target="_blank"
                      >twitter.com/TH_Nuernberg</a
                    >
                  </li>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://www.youtube.com/user/THNuernberg"
                      target="_blank"
                      >www.youtube.com/user/THNuernberg</a
                    >
                  </li>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://www.facebook.com/thnuernberg"
                      target="_blank"
                      >www.facebook.com/thnuernberg</a
                    >
                  </li>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://www.instagram.com/th_nuernberg/"
                      target="_blank"
                      >www.instagram.com/th_nuernberg/</a
                    >
                  </li>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://www.xing.com/companies/technischehochschulenürnberg"
                      target="_blank"
                      >www.xing.com/companies/technischehochschulenürnberg</a
                    >
                  </li>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://www.xing.com/communities/groups/th-nuernberg-1054832"
                      target="_blank"
                      >www.xing.com/communities/groups/th-nuernberg-1054832</a
                    >
                  </li>
                </ul>
                <p>
                  At present, we assume that we are not subject to any joint responsibility under data protection law in
                  so far as your data are processed by these providers for the purposes defined here.
                </p>
                <h4>Purposes and legal basis and regulations for processing in accordance with Article 6 GDPR</h4>
                <p>
                  We provide our services, administrative services, and information for the public about our activities
                  on our website in accordance with Article 2, paragraph 6 BayHSchG, and Article 4, paragraph 1,
                  sentences 1 and 2 BayEGovG.
                </p>
                <p>
                  Our social media profiles form part of our public relations activities. Our aim is to provide
                  information in a manner that is appropriate to the target groups and to interact with you, Article 2,
                  paragraph 6 BayHSchG. We make it possible for you to contact us quickly via electronic means and to
                  communicate directly using your choice of media, Section 5, paragraph 1, no. 2 TMG.
                </p>
                <p>
                  We shall disclose content and contributions or queries that violate third-party rights or constitute a
                  criminal or administrative offence, or fail to fulfil the conduct required by law or by contract, by
                  forwarding them to the competent authority or the social media provider, and block or delete them.
                </p>
                <p>
                  We use cookies, protocol files, statistics of social media providers, and the web analysis tool Matomo
                  to produce business statistics, carry out organisational reviews, perform tests or maintenance of our
                  web service, and guarantee network and information security in accordance with Article 6, para. 1
                  BayDSG [Bavarian Data Protection Act]; Section 13, para. 7 TMG [Telemedia Act]; Art. 11 para. 1
                  BayEGovG [Bavarian E-Government Act]. We anonymize or pseudonymize personal data unless this affects
                  the purpose of processing.
                </p>
                <h4>Right to information and rectifications</h4>
                <p>In accordance with the General Data Protection Act, you are entitled to the following rights:</p>
                <ul>
                  <li>
                    If your personal data are being processed, you have the right to obtain information regarding the
                    data stored about you (Article 15 GDPR).
                  </li>
                  <li>
                    Should inaccurate personal data be being processed, you are entitled to have them rectified (Article
                    16 GDPR).
                  </li>
                  <li>
                    Should the statutory conditions exist, you may request the erasure or restriction of processing of
                    data, or file an objection to processing (Articles 17, 18 and 21 GDPR).
                  </li>
                  <li>
                    If you have agreed to data processing or a data processing agreement exists and data processing is
                    being carried out using an automated process, you are entitled to data portability if required
                    (Article 20 GDPR)
                  </li>
                </ul>
                <p>
                  Should you have any further questions regarding collection of personal data, you are welcome to
                  contact the University’s Data Protection Officer in accordance with the EU GDPR.
                </p>
                <p>
                  Should you exercise any of the aforementioned rights, the public office will verify whether the
                  statutory requirements for this have been fulfilled.
                </p>
                <p>Individuals also have a right of complaint to the Bavarian Federal State Data Protection Officer.</p>
                <p>
                  We ensure compliance with the data protection provisions on all parts of our platform and in all parts
                  of our University. If you have any questions, you are also welcome to contact us directly:
                  <a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="mailto:datenschutz@th-nuernberg.de"
                    ><strong
                      ><em
                        >datenschutz<span class="fa fa-at"><span class="sr-only">at</span></span
                        >th-nuernberg<span class="fa fa-circle dot-subst"><span class="sr-only">Punkt</span></span
                        >de</em
                      ></strong
                    ></a
                  ><br /><br />Version date: 3 July 2018<br /><strong
                    ><em>University Data Protection Officer</em></strong
                  ><br /><br />
                </p>
              </div>
            </div>
          </section>
        </div>
        <div v-else class="col-content">
          <section id="c42462" class="content content-text">
            <div class="container">
              <div class="content-inner">
                <h2>Datenschutzerklärung</h2>
                <p><strong>Dies ist die Datenschutzerklärung von:</strong></p>
                <p>
                  Technische Hochschule Nürnberg Georg Simon Ohm<br />Keßlerplatz 12<br />90489 Nürnberg<br />- im
                  folgenden TH Nürnberg genannt -
                </p>
                <p>
                  Die TH Nürnberg nimmt den Datenschutz ernst. Die Erhebung Ihrer Daten erfolgt im Rahmen der
                  gesetzlichen Vorschriften. Über diese können Sie sich unter
                  <a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="https://www.datenschutz.de/"
                    title="Opens internal link in current window"
                    target="_blank"
                    class="external-link-new-window"
                    >www.datenschutz.de</a
                  >
                  umfassend informieren.
                </p>
                <p>
                  Der Datenschutzbeauftragte der TH Nürnberg, Michael Günther, ist erreichbar unter
                  <a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="mailto:datenschutz@th-nuernberg.de"
                    title="Opens internal link in current window"
                    class="mail"
                    >datenschutz<span class="fa fa-at"><span class="sr-only">at</span></span
                    >th-nuernberg<span class="fa fa-circle dot-subst"><span class="sr-only">Punkt</span></span
                    >de</a
                  >
                </p>
              </div>
            </div>
          </section>
          <section id="c42461" class="content content-text">
            <div class="container">
              <div class="content-inner">
                <p><strong>Grundsätzlich gilt:</strong></p>
                <p>
                  Um die Sicherheit Ihrer Daten angemessen bei der Übertragung zu schützen, verwenden wir orientiert am
                  aktuellen Stand der Technik entsprechende Verschlüsselungsverfahren (z. B. SSL/TLS) und gesicherte
                  technische Systeme.
                </p>
                <p>
                  Für die Webseiten wird als aktive Komponente Javascript verwendet. Sollten Sie diese Funktion in Ihrem
                  Browser abgestellt haben, erhalten Sie einen entsprechenden Hinweis, die Funktion zu aktivieren. Beim
                  Zugriff eines Nutzers auf eine Seite der TH Nürnberg und beim Abruf einer Datei können über diesen
                  Vorgang Daten in einer Protokolldatei gespeichert werden. Im Einzelnen wird dann folgender Datensatz
                  gespeichert:
                </p>
                <ul>
                  <li>Name der abgerufenen Datei</li>
                  <li>Datum und Uhrzeit des Abrufs</li>
                  <li>Übertragene Datenmenge</li>
                  <li>Meldung, ob der Abruf erfolgreich war</li>
                  <li>Beschreibung des Typs des verwendeten Webbrowsers</li>
                  <li>anfragende Domain</li>
                </ul>
                <p>
                  Eine Löschung dieser Statistik-Rohdaten erfolgt nach Abschluss des durch den Nutzer veranlassten
                  Vorgangs.
                </p>
                <p>
                  Für die Nutzung der Seiten der TH Nürnberg kann es erforderlich sein, dass von den Servern der TH
                  Nürnberg Cookies gesetzt werden. Es werden zwei Arten von Cookies eingesetzt.
                </p>
                <ul>
                  <li>
                    Session-Cookies werden zum Teil für die Navigation auf den Portalen der TH Nürnberg benötigt.
                    Session Cookies verlieren ihre Gültigkeit, wenn der Browser geschlossen wird oder eine bestimmte
                    Zeit keine Aktivität auf den Seiten der TH Nürnberg stattfindet. Bei einer Nutzung des
                    personalisierten Bereichs des TH Nürnberg – Portals muss dann ein erneutes Einloggen erfolgen.
                  </li>
                  <li>
                    Cookies zur Bereitstellung verschiedener Dienste haben einen definierten Gültigkeitszeitraum, der
                    jeweils abhängig von der speziellen Anwendung ist.
                  </li>
                </ul>
                <p>
                  <strong>Regelfristen zur Datenlöschung:</strong> Aufgrund gesetzlicher Bestimmungen gelten bestimmte
                  Aufbewahrungspflichten und -fristen. Nach Ablauf dieser Fristen werden die entsprechenden Daten
                  routinemäßig gelöscht. Im Übrigen werden personenbezogene Daten gelöscht, sobald sie zur Erfüllung des
                  Zwecks, zu dem sie erhoben wurden, nicht mehr erforderlich sind oder die Legitimationsgrundlage für
                  den Datenumgang entfällt (z. B. durch den Widerruf einer Einwilligung). So werden auch beim
                  Ausscheiden einer Mitarbeiterin/eines Mitarbeiters aus der Hochschulorganisation, innerhalb eines
                  angemessen Zeitraums alle hierzu gehörenden Einträge aus der Personendatenbank gelöscht, alle
                  sonstigen redaktionellen Einträge auf Hochschulwebseiten hingegen erst auf Widerruf. Für Löschungen
                  personenbezogener Einträge und Verlinkungen zu Internetsuchmaschinen anderer Verantwortlichen ist
                  grundsätzlich jeder selbst verantwortlich.
                </p>
                <p>
                  <strong>Nutzungsanalyse mit Matomo: </strong>Die TH Nürnberg nutzt zur statistischen Auswertung dieses
                  Webangebots die Open-Source-Software Matomo. Hierbei anfallenden Informationen werden nur innerhalb
                  der TH Nürnberg verarbeitet und ausgewertet.
                </p>
                <p>
                  Erfasste Daten werden nicht an Dritte weitergegeben. Sie dienen der Identifikation und Verbesserung
                  relevanter Inhalte des Internetangebotes. IP-Adressen werden in diesem Zusammenhang sofort nach der
                  Verarbeitung und vor deren Speicherung anonymisiert.
                </p>
                <p>
                  Matomo - ehemals Piwik - ist nach den Empfehlungen des Unabhängigen Landeszentrums für Datenschutz
                  (ULD) Schleswig-Holstein konfiguriert und folgt den geltenden Datenschutzbestimmungen.
                </p>
                <p>
                  Durch die Nutzung dieses Internetangebots erklären Sie sich mit der Bearbeitung der über Sie erhobenen
                  Daten in der zuvor beschriebenen Art und Weise und nur zu dem zuvor benannten Zweck einverstanden. Sie
                  können die Nutzungsanalyse durch Matomo mit der nachfolgend eingeblendeten Schaltfläche unterbinden.
                </p>
                <p>
                  Sie können sich hier entscheiden, ob in Ihrem Browser ein eindeutiger Webanalyse-Cookie abgelegt
                  werden darf, um dem Betreiber der Website die Erfassung und Analyse verschiedener statistischer Daten
                  zu ermöglichen.
                </p>
                <p>
                  Wenn Sie sich dagegen entscheiden möchten, klicken Sie auf dem Matomo Banner auf ablehnen, um den
                  Matomo-Deaktivierungs-Cookie in Ihrem Browser abzulegen.
                </p>
              </div>
            </div>
          </section>
          <section id="c42459" class="content content-text">
            <div class="container">
              <div class="content-inner">
                <p>
                  Die gesammelten Daten dienen der Optimierung von Navigation und Inhalten auf den Seiten der TH
                  Nürnberg. Die Untersuchung der Daten erfolgt ganzheitlich, d.h. eine Auswertung von User basierenden
                  Einzeldaten wird explizit nicht durchgeführt. Die gesammelten Daten werden externen Dritten nicht
                  zugeführt.
                </p>
                <p>
                  Die im Rahmen der Registrierung von Nutzern gemachten Angaben werden in anonymisierter Form zu
                  statistischen Zwecken von der TH Nürnberg ausgewertet. Ein Verkauf von Adressen an Dritte findet nicht
                  statt.
                </p>
                <p>
                  User, die sich auf dem Portal der TH Nürnberg registrieren, sind nicht mehr anonym. Bei jedem
                  Einlog-Vorgang auf unseren Seiten können die User die Dienste der TH Nürnberg nutzen, in Abhängigkeit
                  des gewählten Service und der User-Berechtigung. Wendet sich ein registrierter User an den IT-Support
                  der TH Nürnberg, wird ein Ticket über den Vorfall erstellt. Dieses Ticket wird gespeichert, um bei
                  wiederholten Anfragen des Kunden eine Beratungshistorie für eine schnelle Bearbeitung für den Kunden
                  erreichen zu können.
                </p>
                <p>
                  Das Mailsystem der Hochschule verfügt über zentrale Mechanismen, die die Mailboxen der
                  Hochschulangehörigen vor Spam und Viren schützen.<br />Der zentrale Spamschutz besteht aus mehreren
                  Schritten:
                </p>
                <p>&nbsp;</p>
                <p><em>1. Schritt: Blacklist</em></p>
                <p>
                  E-Mails, die von Absendern kommen, die als Spammer oder als Versender von Schadsoftware bekannt sind
                  und die deswegen auf einer Blackliste geführt werden, werden abgewiesen.<br />Die Zentrale IT nutzt zu
                  diesem Zweck die Blackliste einer externen, auf Spamvermeidung spezialisierten Organisation.<br /><br />
                </p>
                <p><em>2. Schritt: Blocking</em></p>
                <p>
                  Danach wird die E-Mail und der E-Mail-Anhang auf Schadsoftware und Viren untersucht. E-Mails, die
                  Viren enthalten, werden entfernt.<br />Zusätzlich wird die Absenderadresse geprüft. Handelt es sich um
                  eine TH-Adresse, die von außen an der Hochschule eingeht, wird diese E-Mail ebenfalls entfernt, da
                  davon auszugehen ist, dass es sich um eine Adressfälschung handelt.<br /><br />
                </p>
                <p><em>3. Schritt: Bewertung der Spam-Wahrscheinlichkeit</em></p>
                <p>
                  Im letzten Schritt wird die E-Mail nach typischen Spam-Merkmalen untersucht und bewertet.<br />Ergibt
                  die Bewertung, dass es sich bei der E-Mail mit hoher Wahrscheinlichkeit (&gt;60%) um eine Werbe- oder
                  Spam-Mail handelt, dann wird die E-Mail in Quarantäne genommen.<br />Hinweis: Die Spam-Merkmale gibt
                  eine externe, auf Spamvermeidung spezialisierte Organisation vor. <br />Über eine Web-Oberfläche haben
                  Hochschulangehörige die Möglichkeit, die E-Mails, die in Quarantäne genommen wurden, zu überprüfen und
                  gegebenenfalls in Ihren Posteingang zu holen.<br /><br />
                </p>
                <p>
                  Die TH Nürnberg stellt im Rahmen von Serviceangeboten teilweise Hosting-Kapazitäten zur Verfügung. Für
                  die Nutzung dieser Systeme gelten die AGB der TH Nürnberg.
                </p>
                <p>
                  Die Mitarbeiter der TH Nürnberg sind zur Verschwiegenheit über personenbezogene Daten verpflichtet.
                  Eine Weitergabe dieser Daten an Dritte erfolgt nur, wenn dies für die Erfüllung dienstlicher Aufgaben
                  notwendig ist. Solche Dritte sind ebenfalls zur Beachtung des Datenschutzes der Nutzer verpflichtet.
                </p>
                <p>
                  Alle unter "*.th-nuernberg.de" befindlichen Daten, die sich auf unseren Servern befinden und dort
                  "gehostet" (also aufbewahrt) werden, sind durch Sicherheitssysteme vor dem Zugriff Unberechtigter
                  gesichert. Mitarbeiter der TH Nürnberg und ihrer System-Dienstleister überprüfen die Wirksamkeit des
                  Schutzes.
                </p>
                <p>
                  Nach Verlassen einer Seite (beispielsweise über das Anklicken unserer Bannerwerbung) können von der
                  angeklickten Zielseite Cookies gesetzt werden. Für diese ist die TH Nürnberg rechtlich nicht
                  verantwortlich. Zu der Benutzung solcher Cookies und der darauf gespeicherten Informationen durch
                  unsere Werbepartner vergleichen Sie bitte deren Datenschutzerklärungen.
                </p>
                <p>
                  Die TH Nürnberg weist darauf hin, dass die Nutzung des personalisierten Bereiches des Portals
                  grundsätzlich immer über gesicherte Zugänge erfolgen sollte (VPN). Nur so kann sichergestellt werden,
                  dass über das Internet übertragene personenbezogene Daten zwischen den Nutzern und den Servern der TH
                  Nürnberg durch Dritte nicht eingesehen werden können.
                </p>
                <p>
                  Alle betriebenen Server, auf denen personenbezogene Daten für die Nutzer der TH Nürnberg verarbeitet
                  oder erfasst werden, stehen in der Bundesrepublik Deutschland.
                </p>
                <p>
                  Die Sicherheitseinstellungen des Browsers bieten die Möglichkeit, das Speichern von Cookies zuzulassen
                  oder zu verbieten. Weitere Informationen zur Verwendung von Cookies finden sich auch im Internet auf
                  den Seiten des Bundesamtes für Sicherheit in der Informationstechnik (<a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="http://www.bsi.de"
                    title="Opens internal link in current window"
                    target="_blank"
                    class="external-link-new-window"
                    >www.bsi.de</a
                  >).<br />Beauftragt die TH Nürnberg für die Durchführung von bestimmten Dienstleistungen
                  Partnerfirmen, so werden in den Verträgen mit den Partnern die Datenschutzbestimmungen übertragen und
                  die Partner auf die Einhaltung des Datenschutzes verpflichtet.
                </p>
                <p>
                  <strong>Kontaktaufnahme mit der TH Nürnberg über Kontaktformulare </strong>für Veranstaltungen
                  und/oder Programme der TH Nürnberg sowie zur Fehlerkorrektur auf den Webseiten der TH Nürnberg: Mit
                  unseren Kontaktformularen können Sie eine Anfrage oder Nachricht an uns richten. Damit wir daraufhin
                  Kontakt mit Ihnen aufnehmen können, ist die Angabe Ihres Namens und Ihrer E-Mail-Adresse erforderlich.
                  Weitergehende personenbezogene Daten können Sie uns je nach Formular freiwillig mitteilen. Eine
                  Nutzung zu einem anderen Zweck oder eine Datenweitergabe an Dritte findet nicht statt.
                </p>
                <h4>Veranstaltungen, Presse- und Öffentlichkeitsarbeit</h4>
                <p>
                  Die TH Nürnberg tritt auch als Organisator oder Mitorganisator diverser Veranstaltungen auf.<br />Im
                  Falle einer Einladung zu oder Teilnahme an einer Veranstaltung verarbeitet die TH Nürnberg
                  personenbezogene Daten (Name, Adresse etc.). Dies kann über verschiedene Kommunikationswege erfolgen,
                  z.B. durch Ausfüllen eines Formulars, eines Webformulars, per E-Mail, per Telefon.
                </p>
                <p>
                  Welche personenbezogenen Daten dabei an die TH Nürnberg übermittelt werden, ergibt sich aus dem
                  jeweiligen Formular, der jeweiligen Eingabemaske bzw. den in einem etwaigen Gespräch abgefragten
                  Daten.
                </p>
                <h5>Datenerhebung von Begleitpersonen</h5>
                <p>
                  Für die ordnungsgemäße Abwicklung der Veranstaltung werden dabei auch Daten von Begleitpersonen der
                  eingeladenen Teilnehmer erhoben und verarbeitet. Diesen stehen ebenso wie allen anderen von
                  Datenerhebungen Betroffenen die hier genannten Rechte zu, insbesondere auf Auskunft über Art und
                  Umfang der gespeicherten Daten, Widerspruch gegen die Verarbeitung und Löschung der Daten. Insofern
                  wird auf die Ausführungen unter Auskunftsrecht und Berichtigungen verwiesen.
                </p>
                <h5>Weiteres Verfahren bei diesen Datenerhebungen</h5>
                <p>
                  Die personenbezogenen Daten werden nicht unbefugt an Dritte übermittelt, sondern für die interne
                  Verwendung bei der TH Nürnberg und für den Zweck der Organisation und Abwicklung von Veranstaltungen
                  (etwa Erstellung von Gästelisten, Ermöglichung von Zugangskontrollen etc.) gespeichert und
                  verarbeitet. Die TH Nürnberg kann die Weitergabe an einen oder mehrere Auftragsverarbeiter
                  veranlassen, der die personenbezogenen Daten im Auftrag der TH Nürnberg nur für eine interne
                  Verwendung, die der TH Nürnberg zuzurechnen ist, nutzt.
                </p>
                <p>
                  Je nach Art der Veranstaltung tritt die TH Nürnberg neben einem weiteren Kooperationspartner als
                  Mitveranstalter auf. In diesen Fällen werden die zu Veranstaltungszwecken erhobenen Daten an unsere
                  Kooperationspartner übermittelt, wobei diese die Daten ebenfalls ausschließlich zu diesem Zweck der
                  ordnungsgemäßen Abwicklung der Veranstaltung verwenden dürfen. Welche Kooperationspartner dies im
                  Einzelfall sind, wird gesondert im Rahmen der Organisation der Veranstaltung jeweils mitgeteilt.
                </p>
                <p>
                  Die Daten werden nur so lange gespeichert, wie dies für die Organisation und Abwicklung der
                  Veranstaltungen sowie für unsere Aufgabenwahrnehmung im Bereich der Öffentlichkeitsarbeit erforderlich
                  ist.
                </p>
                <p>
                  Als Empfänger von Anschreiben/Einladungen können Sie jederzeit der Zusendung weiterer
                  Anschreiben/Einladungen widersprechen.
                </p>
                <h5>Bild-, Ton- und Fotoaufnahmen</h5>
                <p>
                  Im Rahmen der Aufgabenwahrnehmung von Presse- und Öffentlichkeitsarbeit der TH Nürnberg werden bei
                  Veranstaltungen und Terminen ggf. Film-, Ton- und Fotoaufnahmen aufgenommen und verwendet, auf denen
                  Sie ggf. erkennbar zu sehen sind. Das erstellte Bild- und/oder Filmmaterial darf vergütungsfrei
                  zeitlich, räumlich und inhaltlich unbeschränkt verwertet werden. Dem können Sie ebenfalls
                  widersprechen. Bitte nutzen Sie für Ihren Widerspruch genannte Kontaktdaten.
                </p>
                <h4>Datenschutzhinweis zu den sozialen Medien</h4>
                <p>
                  Über einen Klick auf die Social-Media-Buttons auf den Websites des Internetangebotes der TH Nürnberg
                  gelangen Sie zum Auftritt der TH Nürnberg in den sozialen Medien. Das Internetangebot der TH Nürnberg
                  wird damit verlassen. In den sozialen Netzwerken sind die persönlichen Daten selbstständig von jeder
                  Nutzerin und jedem Nutzer zu schützen. Zu beachten sind die dortigen Datenschutzbestimmungen sowie die
                  Einstellungen zur Privatsphäre.
                </p>
                <p>Und als Ergänzung soweit wir personenbezogene Daten in eigener Verantwortung verarbeiten für:</p>
                <ul>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://twitter.com/TH_Nuernberg"
                      target="_blank"
                      >twitter.com/TH_Nuernberg</a
                    >
                  </li>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://www.youtube.com/user/THNuernberg"
                      target="_blank"
                      >www.youtube.com/user/THNuernberg</a
                    >
                  </li>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://www.facebook.com/thnuernberg"
                      target="_blank"
                      >www.facebook.com/thnuernberg</a
                    >
                  </li>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://www.instagram.com/th_nuernberg/"
                      target="_blank"
                      >www.instagram.com/th_nuernberg/</a
                    >
                  </li>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://www.xing.com/companies/technischehochschulenürnberg"
                      target="_blank"
                      >www.xing.com/companies/technischehochschulenürnberg</a
                    >
                  </li>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://www.xing.com/communities/groups/th-nuernberg-1054832"
                      target="_blank"
                      >https://www.xing.com/communities/groups/th-nuernberg-1054832</a
                    >
                  </li>
                  <li>
                    <a
                      @click="matomo_clicktracking('click_link', $event.target.href)"
                      href="https://www.linkedin.com/school/technische-hochschule-nürnberg-georg-simon-ohm"
                      target="_blank"
                      >https://www.linkedin.com/school/th-nuernberg</a
                    >
                  </li>
                </ul>
                <p>
                  Wir gehen derzeit davon aus, dass wir keine datenschutzrechtliche Mitverantwortung unterliegen, soweit
                  Ihre Daten durch diese Anbieter zu von diesen festgelegten Zwecken verarbeitet werden.
                </p>
                <h4>Temporäre Einbindung von umap/OpenStreetMap</h4>
                <p>
                  Wir verwenden temporär auf unserer Webseite einen Kartenausschnitt von umap (<a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="/(https://umap.openstreetmap.de"
                    >https://umap.openstreetmap.de</a
                  >), um für Sie die verschiedenen Standorte und Projektflächen mit dazugehörenden Informationen
                  darzustellen.
                </p>
                <p>
                  Bei umap handelt es sich um ein Open-Source-Mapping-Werkzeug, welches auf Basis des französischen
                  Angebots von OpenStreetMap funktioniert. Damit Ihnen die Karte angezeigt werden kann, wird Ihre
                  IP-Adresse an OpenStreetMap weitergeleitet. Rechtsgrundlage für die Übermittlung der IP-Adresse ist
                  Art. 6 Abs. 1 S. 1 lit. f DSGVO. Unser berechtigtes Interesse besteht darin, Ihnen einen komfortablen
                  Verbindungsaufbau zum Dienst zu ermöglichen. Weitere Informationen zur Datenverarbeitung durch
                  OpenStreetMap finden Sie auf der Datenschutzseite von OpenStreetMap, allerdings nur auf Englisch:
                  <a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="https://wiki.osmfoundation.org/wiki/Privacy_Policy"
                    target="_blank"
                    >https://wiki.osmfoundation.org/wiki/Privacy_Policy</a
                  >&nbsp; <br />Anbieter von OpenStreetMap ist die Openstreetmap Foundation: Openstreetmap Foundation,
                  132 Maney Hill Road, Sutton Coldfield, West Midlands, B72 1JU, United Kingdom
                </p>
                <h4>&nbsp;</h4>
                <h4>Zwecke und Rechtsgrundlagen der Verarbeitung nach Art. 6 DSGVO</h4>
                <p>
                  Wir bieten gemäß Art. 2 Abs. 6 BayHSchG, Art. 4 Abs. 1 S. 1 und 2 BayEGovG auf unseren Webseiten
                  unsere Dienste und Verwaltungsleistungen sowie Informationen für die Öffentlichkeit über unsere
                  Tätigkeit.
                </p>
                <p>
                  Unsere Social Media Auftritte sind Teil unserer Öffentlichkeitsarbeit. Unser Bestreben ist es,
                  zielgruppengerecht zu informieren und sich mit Ihnen auszutauschen, Art. 2 Abs. 6 BayHSchG. Wir
                  ermöglichen Ihnen eine schnelle elektronische Kontaktaufnahme und unmittelbare Kommunikation über die
                  Medien Ihrer Wahl, § 5 Abs. 1 Nr. 2 TMG.
                </p>
                <p>
                  Inhalte und Beiträge, Anfragen, die Rechte Dritter verletzen oder die den Tatbestand einer Straftat
                  oder Ordnungswidrigkeit erfüllen, gesetzlichen oder vertraglichen Verhaltenspflicht nicht entsprechen,
                  legen wir durch Übermittlung an die zuständige Behörde bzw. dem Social-Media-Dienst offen und
                  blockieren oder löschen diese.
                </p>
                <p>
                  Cookies, Protokolldateien, Statistiken der Social Media Anbieter, und das Webanalyse-Tool Matomo
                  verwenden wir zur Erstellung von Geschäftsstatistiken, zur Durchführung von
                  Organisationsuntersuchungen, zur Prüfung oder Wartung unseres Webdienstes und zur Gewährleistung der
                  Netz- und Informationssicherheit gemäß Art. 6 Abs. 1 BayDSG, § 13 Abs. 7 TMG, Art. 11 Abs. 1 BayEGovG.
                  Soweit der Verarbeitungszweck nicht beeinträchtigt wird, anonymisieren oder pseudonymisieren wir
                  personenbezogene Daten.
                </p>
                <h4>Auskunftsrecht und Berichtigungen</h4>
                <p>Nach der Datenschutz-Grundverordnung stehen Ihnen folgende Rechte zu:</p>
                <ul>
                  <li>
                    Werden Ihre personenbezogenen Daten verarbeitet, so haben Sie das Recht, Auskunft über die zu Ihrer
                    Person gespeicherten Daten zu erhalten (Art. 15 DSGVO).
                  </li>
                  <li>
                    Sollten unrichtige personenbezogene Daten verarbeitet werden, steht Ihnen ein Recht auf Berichtigung
                    zu (Art. 16 DSGVO).
                  </li>
                  <li>
                    Liegen die gesetzlichen Voraussetzungen vor, so können Sie die Löschung oder Einschränkung der
                    Verarbeitung verlangen sowie Widerspruch gegen die Verarbeitung einlegen (Art. 17, 18 und 21 DSGVO).
                  </li>
                  <li>
                    Wenn Sie in die Datenverarbeitung eingewilligt haben oder ein Vertrag zur Datenverarbeitung besteht
                    und die Datenverarbeitung mithilfe automatisierter Verfahren durchgeführt wird, steht Ihnen
                    gegebenenfalls ein Recht auf Datenübertragbarkeit zu (Art. 20 DSGVO).
                  </li>
                </ul>
                <p>
                  Bei weiteren Fragen zur Erhebung von personenbezogenen Daten steht Ihnen nach EU-DSGVO der
                  Datenschutzbeauftragte der Hochschule zur Verfügung.
                </p>
                <p>
                  Sollten Sie von Ihren oben genannten Rechten Gebrauch machen, prüft die öffentliche Stelle, ob die
                  gesetzlichen Voraussetzungen hierfür erfüllt sind.
                </p>
                <p>Weiterhin besteht ein Beschwerderecht beim Bayerischen Landesbeauftragten für den Datenschutz.</p>
                <p>
                  Wir kümmern uns um die Einhaltung der Datenschutzbestimmungen in allen Bereichen unserer Plattform und
                  unserer Hochschule. Wenn Sie Fragen haben, können Sie sich auch direkt an uns wenden:
                  <strong><em>datenschutz@th-nuernberg.de</em></strong
                  ><br /><br /><em>Stand: 26. November 2020</em><br /><strong
                    ><em>Datenschutzbeauftragter der Hochschule</em></strong
                  ><br /><br />
                </p>
              </div>
            </div>
          </section>
          <section id="c97260" class="content content-accordion">
            <div class="container">
              <div class="content-inner">
                <h3>Datenschutzhinweise und Datenschutzerklärungen für spezielle Zielgruppen</h3>
                <div class="panel-group" role="tablist" id="accordion-97260">
                  <div class="panel panel-default">
                    <div class="panel-heading" role="tab" id="tab-97260-1-heading">
                      <h4 class="panel-title">
                        <a data-toggle="collapse" data-parent="#accordion-97260" href="#tab-97260-1" class="collapsed">
                          Datenschutzhinweise für Studierende und Studieninteressierte
                        </a>
                      </h4>
                    </div>
                    <div
                      class="panel-collapse collapse"
                      role="tabpanel"
                      aria-labelledby="tab-97260-1-heading"
                      id="tab-97260-1"
                    >
                      <div class="panel-body">
                        <section id="c97261" class="content content-text">
                          <div class="container">
                            <div class="content-inner">
                              <p>
                                Datenschutz ist für die Technische Hochschule Nürnberg Georg Simon Ohm ein großes
                                Anliegen und ihre gesetzliche Verpflichtung. Um die Sicherheit persönlicher Daten
                                angemessen bei der Übertragung zu schützen, verwendet die Technische Hochschule Nürnberg
                                entsprechende Verschlüsselungsverfahren (z.B. SSL/TLS) und gesicherte technische
                                Systeme.
                              </p>
                              <h4>1. Name und Anschrift des Verantwortlichen</h4>
                              <p>
                                Der Verantwortliche im Sinne der EU‐Datenschutzgrundverordnung (DSGVO) und anderer
                                nationaler Datenschutzgesetze der Mitgliedsstaaten sowie sonstiger
                                datenschutzrechtlicher Bestimmungen ist die:<br />Technische Hochschule Nürnberg Georg
                                Simon Ohm<br />Keßlerplatz 12<br />90489 Nürnberg<br />Telefon: + 49 911/5880-0<br />Telefax:
                                + 49 911/5880-8309<br />E-Mail: info@th-nuernberg.de<br />Die Technische Hochschule
                                Nürnberg Georg Simon Ohm ist eine Körperschaft des Öffentlichen Rechts. Sie wird durch
                                Ihren Präsidenten Prof. Dr. Niels Oberbeck gesetzlich vertreten.
                              </p>
                              <h4>2. Name und Anschrift des Datenschutzbeauftragten</h4>
                              <p>
                                Den Datenschutzbeauftragten der Technischen Hochschule Nürnberg können Sie neben der o.
                                g. Postanschrift unter folgenden Kontaktdaten erreichen:<br />Telefon: 0911 / 5880 4200
                                <br />E-Mail: datenschutz@th-nuernberg.de<br /><br />
                              </p>
                              <h4>3. Zwecke und Rechtsgrundlagen der Verarbeitung</h4>
                              <p>
                                Die Technische Hochschule Nürnberg nutzt die erhobenen persönlichen Daten, um die
                                Studienplatzbewerbung im Rahmen der gesetzlichen Vorgaben zu bearbeiten ebenso wie für
                                das an eine erfolgreiche Studienplatzbewerbung anschließende Immatrikulationsverfahren.
                                Bei einer Immatrikulation an der TH Nürnberg werden persönliche Daten im weiteren
                                Verlauf für die Studierenden- und Prüfungsverwaltung, zur Unterstützung für die
                                Bearbeitung von internationalen Angelegenheiten wie Auslandssemester/Auslandspraktika
                                sowie für Stipendienangelegenheiten bzw. als Grundlage für die Talentförderung
                                übernommen. Im Rahmen der Betreuung internationaler Studierender erfolgt zudem eine
                                Nutzung der persönlichen Daten, um die Zielgruppe während ihres Studienverlaufs über
                                bedarfsgerechte Angebote und Veranstaltungen zu informieren.<br />Wenn Studierende nach
                                ihrem Abschluss mit der Technischen Hochschule Nürnberg als Alumni in Kontakt bleiben
                                wollen, ist eine separate Erklärung / Anmeldung erforderlich: Nur dann werden die Daten
                                für passgenaue Alumniangebote verwendet.<br />Außerdem nutzt die Technische Hochschule
                                Nürnberg die erhobenen Daten um Systemzugänge (Netzwerk, Online-Portale,
                                Lernplattformen, Bibliotheksnutzung, Raumnutzungen) zu steuern.<br />Im
                                Bewerbungsverfahren werden persönliche Daten ausschließlich für den Kontakt und die
                                Abwicklung des Bewerbungsverfahrens eingesetzt.<br />In der Studierenden- und
                                Prüfungsverwaltung werden die Daten für den Kontakt, für das Antragsmanagement
                                (Beurlaubungen, Fristen, Anerkennung etc.) sowie für die Praktikums-, Gebühren- und
                                Prüfungsverwaltung im Rahmen der rechtlichen Vorgaben genutzt.<br />Im Rahmen der
                                Stipendienangelegenheiten erfasst die TH Nürnberg über die Hochschule abzuwickelnde
                                Stipendienanträge (z.B. Deutschlandstipendium) und nutzt die vorhandenen Daten für die
                                zielgerichtete Information über Stipendienprogramme, die Talentförderung und die Vergabe
                                von Preisen an Studierende und AbsolventInnen. In einigen externen Förderprogrammen
                                haben die Hochschulen ein Vorschlagsrecht zu nach den jeweiligen Kriterien geeigneten
                                Studierenden. Dazu gehören ggf. vorläufige Prüfungsergebnisse aus dem
                                Campus-Managementsystem. Die Technische Hochschule Nürnberg ermittelt in den Systemen
                                die Studierenden, die die Kriterien der Förderprogramme am besten erfüllen; ein
                                Vorschlag mit der Übermittlung persönlicher Daten an externe Stipendiengebende erfolgt
                                nur mit einer Einwilligung.<br />BewerberInnen und immatrikulierte Studierende erhalten
                                von der Technischen Hochschule Nürnberg jeweils passwortgeschützte Systemzugänge für die
                                digitale Erledigung von Bewerbungen sowie Anträgen und Verfahren in dem Portal für
                                BewerberInnen und Studierende: Die Hochschule protokolliert die Zugriffe und
                                Aktivitäten, um jederzeit die Rechtmäßigkeit der Zugriffe nachvollziehen und die
                                Aktivitäten nachweisen zu können. Darüber hinaus erfolgt keine Nutzung der
                                Protokolldaten. <br />Rechtsgrundlage für die Datenerhebung ist Art.6 Abs. 3 Ziff b
                                DSGVO i.V.m. Art. 42 Bayerisches Hochschulgesetz (BayHSchG), dem Bayerischen
                                Hochschulzulassungsgesetz (BayHZG) und die Satzung über das Verfahren der
                                Hochschulzulassung, Immatrikulation, Rückmeldung, Beurlaubung und der Exmatrikulation an
                                der TH Nürnberg Georg Simon Ohm (HZIS).<br />Die Speicherung von privaten
                                E-Mail-Adressen sowie der privaten Telefonkontaktdaten erfolgt auf Grundlage von Art. 6
                                Abs. 1 lit. e), Abs. 3 Ziff. b) DSGVO i.V.m. Art.4 Abs. 1 BayDSG n.F.: Nach der
                                Immatrikulation bleiben diese Daten nur auf Ihren Wunsch bei der Hochschule erhalten, da
                                sie die Möglichkeit haben Ihre persönlichen Daten selbst zu verwalten. Die
                                Kontaktaufnahme über nicht hochschulinterne Daten erfolgt nur im Ausnahmefall. Die
                                Datenverarbeitung ist daher für die Wahrnehmung einer Aufgabe erforderlich, die dem
                                Verantwortlichen oder der Verantwortlichen übertragen wurde. Da private Kontaktdaten
                                lediglich intern genutzt, intern nur an berechtigte Serviceeinheiten und extern nicht
                                weitergeben werden, stehen dem nicht Interessen an Wahrung der Privatsphäre und Schutz
                                der persönlichen Daten überwiegend entgegen. <br />Studierendendaten können in
                                anonymisierter Form für Forschungszwecke verwendet werden. Hier ist die Rechtsgrundlage
                                Art. 6 Abs 1 lit. c) DSGVO iVm Art. 10 Abs. 1, Art. 42 Abs. 4 BayHschG sowie Art. 6 Abs.
                                1 lit. e) DSGVO i.V.m. Art. 89 DSGVO und Art. 4 Abs.1, Art. 25 BayDSG. Zur Sicherung und
                                Wahrung der Daten werden die Leitlinien zur Sicherung guter wissenschaftlicher Praxis
                                (z. B. definiert durch die Deutsche Forschungsgemeinschaft (DFG), die German Economic
                                Association (GEA), die European Economic Association (EEA) oder die American Economic
                                Association (AEA)) befolgt. <br /><br />
                              </p>
                              <h4>4. EmpfängerInnen oder Kategorien von EmpfängerInnen der personenbezogenen Daten</h4>
                              <p>
                                Die Technische Hochschule Nürnberg gibt Daten nur auf der Grundlage gesetzlicher
                                Ermächtigungen oder mit vorliegendem Einverständnis weiter: Darüber hinaus erfolgt keine
                                Datenweitergabe.<br />Bei Studiengängen, die am bundesweiten Zulassungsabgleich, dem
                                sogenannten dialogorientierten Serviceverfahren (DoSV), teilnehmen, werden
                                Bewerbungsdaten an die für das DoSV zuständige Stiftung für Hochschulzulassung (siehe
                                www.hochschulstart.de ) für den bundesweiten Bewerbungs- und Zulassungsabgleich
                                übermittelt und mit den dort hinterlegten Daten abgeglichen (Rechtsgrundlage § 37 a
                                Bayerische Hochschulzulassungsverordnung).<br />In Studiengängen, die wir gemeinsam mit
                                anderen Hochschulen anbieten bzw. gemeinsam Abschlüsse verleihen, übermitteln wir den
                                Partnerhochschulen Ihre personenbezogenen Daten (als Immatrikulierte bzw. Neben- oder
                                Kooperationshörer), soweit das für die Wahrnehmung des Studienangebots an der
                                Partnerhochschule und die Erstellung von Bescheinigungen und Zeugnissen erforderlich
                                ist. Zu diesen Zwecken verarbeiten wir auch Ihre personenbezogenen Daten, die wir
                                hierfür von den Partnerhochschulen erhalten. Alle beteiligten Hochschulen sind dabei in
                                gleicher Weise auf die Einhaltung des Datenschutzes verpflichtet.<br />Bei
                                Kooperationsstudiengängen mit einem externen Ausbildungspartner existieren
                                Kooperationsverträge zwischen der TH Nürnberg und dem jeweiligen Praxispartner. Im
                                Rahmen der Kooperation werden Informationen bezüglich Ihres Studierendenstatus, Ihres
                                Studienfortschritts und Ihres Ausbildungsstandes zwischen der TH Nürnberg und Ihrer
                                Ausbildungsstätte im Laufe des Studiums ausgetauscht werden.<br />Im Rahmen der
                                Zulassung und des Studienverlaufs erfolgt ein Abgleich persönlicher Daten mit der
                                Krankenkasse (Rechtsgrundlage § 199a SGB V i. V. m. den gemeinsamen Grundsätzen zum
                                elektronischen Studenten-Meldeverfahren des GKV-Spitzenverbandes und der
                                Hochschulrektorenkonferenz) sowie ggfs. eine Datenübermittlung an das Studentenwerk
                                Erlangen-Nürnberg im Zusammenhang mit dort gestellten BAföG-Anträgen (Rechtsgrundlage §§
                                47, 48 Bundesausbildungsförderungsgesetz – BAföG).<br />Das Bibliothekssystem der
                                Technischen Hochschule Nürnberg Georg Simon Ohm wird am Leibniz Rechenzentrum, einem
                                Institut der Bayerischen Akademie der Wissenschaften, gehostet. Die technische Betreuung
                                erfolgt durch die Verbundzentrale der Bayerischen Staatsbibliothek und über die
                                Bibliothek der Technischen Hochschule Nürnberg Georg Simon Ohm.<br />Die Hochschule hat
                                in etlichen Stipendienprogrammen ein Vorschlagsrecht für mögliche KandidatInnen unter
                                den Studierenden: Kontakt- und Leistungsdaten gibt die Hochschule stets nur mit
                                Einwilligung der Betroffenen weiter. Eine Datenweitergabe auch ohne Kenntnis ist
                                zulässig auf der Grundlage des Art. 27 Bayerisches Datenschutzgesetz, BayDSG n.F. zur
                                Vorbereitung und Durchführung staatlicher oder kommunaler Auszeichnungen oder
                                Ehrungen.<br />Die Technische Hochschule Nürnberg betreibt HISinOne als Prüfungs-,
                                Immatrikulations- und Studierendenverwaltungssoftware. Die Systeme, einschließlich der
                                Online-Portale, werden zentral in der Hochschule gehostet und administriert. <br />Die
                                Technische Hochschule Nürnberg Georg Simon Ohm analysiert anonymisierte
                                Studienverlaufsdaten, um Beratungsangebote und Fördermaßnahmen zu optimieren.<br /><br />
                              </p>
                              <h4>5. Geplante Speicherdauer der personenbezogenen Daten</h4>
                              <p>
                                BewerberInnendaten werden ausschließlich zur Bearbeitung von Bewerbungen genutzt. Die
                                Bewerberdaten werden nach Ende des jeweiligen Zulassungsverfahrens spätestens nach sechs
                                Monaten gelöscht (Art. 17 Abs. 1 lit. a DSGVO). Im Fall der Archivwürdigkeit erfolgt die
                                Löschung erst, nachdem die Daten dem Archiv angeboten wurden (Art. 89 DSGVO iVm Art. 26
                                Abs. 6 BayDSG n.F.). Bei Austauschstudierenden gelten andere Aufbewahrungsfristen, die
                                Sie unter dem jeweiligen Bewerberportal „MoveOn“ einsehen können. <br />Von
                                immatrikulierten Studierenden speichert die Technischen Hochschule Nürnberg Georg Simon
                                Ohm die persönlichen Daten für die Dauer des Studiums nach den gesetzlichen Vorgaben:
                              </p>
                              <ul>
                                <li>
                                  Anträge und sonstiger Schriftverkehr wird für die Dauer des Studiums und für sechs
                                  Monate darüber hinaus gespeichert, um den Studienverlauf nachvollziehen und ggfs.
                                  entsprechende Bescheinigungen etc. ausstellen zu können.
                                </li>
                              </ul>
                              <ul>
                                <li>
                                  Prüfungsunterlagen sind nach § 12 der Rahmenprüfungsordnung für die Hochschulen in
                                  Bayern (RaPO) für zwei Jahre aufzubewahren, beginnend mit dem Ablauf des
                                  Kalenderjahres, in dem das Ergebnis der jeweiligen Modulprüfung mitgeteilt wurde.
                                  Prüfungsunterlagen, die Gegenstand eines Widerspruchs- oder Klageverfahrens sind,
                                  werden davon abweichend bis zum rechtskräftigen Abschluss des Verfahrens gespeichert.
                                </li>
                              </ul>
                              <ul>
                                <li>
                                  Eine reduzierte Prüfungsakte wird für die Dauer von 50 Jahren gespeichert mit
                                  Informationen über die Immatrikulationsdauer, die Prüfungsergebnisse, die
                                  Exmatrikulation und die Verleihung des akademischen Grades. Die Aufbewahrungsfrist
                                  beginnt mit dem Ablauf des Kalenderjahres, in welchem die Exmatrikulation erfolgt ist.
                                </li>
                              </ul>
                              <ul>
                                <li>
                                  Persönliche Daten, die Finanztransaktionen betreffen (Studentenwerksbeiträge,
                                  Studiengebühren in den berufsbegleitenden Bachelor- und Masterstudiengängen) werden
                                  auf der Grundlage des Haushalt- und Steuerrechts für die Dauer von zehn Jahren
                                  gespeichert.
                                </li>
                              </ul>
                              <ul>
                                <li>
                                  Daten in den Bibliothekssystemen werden gelöscht nach erfolgter Exmatrikulation und
                                  Löschung des Accounts. Sollte ein Konto noch mit Ausleihen oder Gebühren belastet
                                  sein, werden Daten bis zur Bereinigung des Kontos aufgehoben und unmittelbar danach
                                  gelöscht.
                                </li>
                              </ul>
                              <p>&nbsp;</p>
                              <h4>
                                6. Bereitstellungspflicht der personenbezogenen Daten und mögliche Folgen der
                                Nichtbereitstellung
                              </h4>
                              <p>
                                Gemäß Art. 42 Absatz 4 Bayerisches Hochschulgesetz (BayHSchG) sind Studierende zur
                                Angabe aller persönlichen Daten mit Relevanz für die Abwicklung ihrer Bewerbung und
                                ihres Studiums verpflichtet. Sollten abgefragte, entscheidungsrelevante Daten nicht
                                angegeben worden sein, können darauf beruhende Ansprüche (z.B. auf Zulassung zum
                                Studium, Immatrikulation, Prüfung, Beurlaubung, Fristverlängerungen und Zugänge etc.)
                                verloren gehen.<br /><br />
                              </p>
                              <h4>7. Automatisierte Entscheidungsfindung / Profiling</h4>
                              <p>
                                Im Bereich der Talentförderung an der Technischen Hochschule Nürnberg, für
                                Stipendienvorschläge (s.o.) wertet die TH Nürnberg die Daten der Studierenden nach den
                                jeweiligen Kriterienkatalogen für Stipendien und Talentförderung aus. Auf dieser
                                Grundlage wird ggfs. entsprechend informiert, ggfs. zur Antragstellung aufgefordert bzw.
                                direkt von der Hochschule angesprochen. Unabhängig davon stehen die grundsätzlichen
                                Informationen für die Talentförderung und Stipendienprogramme auf den üblichen Portalen
                                der Anbieter und auf Informationsseiten der Hochschule, für alle Studierenden zur
                                Verfügung.<br /><br />
                              </p>
                              <h4>8. Betroffenenrechte</h4>
                              <p>Nach der Datenschutz-Grundverordnung stehen folgende Rechte zu:</p>
                              <ul>
                                <li>
                                  Werden personenbezogene Daten verarbeitet, so haben Betroffene das Recht, Auskunft
                                  über die zu ihrer Person gespeicherten Daten zu erhalten (Art. 15 DSGVO).
                                </li>
                              </ul>
                              <ul>
                                <li>
                                  Sollten unrichtige personenbezogene Daten verarbeitet werden, steht ein Recht auf
                                  Berichtigung zu (Art. 16 DSGVO).
                                </li>
                              </ul>
                              <ul>
                                <li>
                                  Liegen die gesetzlichen Voraussetzungen vor, so können Sie die Löschung oder
                                  Einschränkung der Verarbeitung verlangen sowie Widerspruch gegen die Verarbeitung
                                  einlegen (Art. 17, 18 und 21 DSGVO). Durch den Widerruf der Einwilligung wird die
                                  Rechtmäßigkeit der aufgrund der Einwilligung bis zum Widerruf erfolgten Verarbeitung
                                  nicht berührt (Art. 7 DSGVO).
                                </li>
                              </ul>
                              <ul>
                                <li>
                                  Wenn Sie in die Datenverarbeitung eingewilligt haben oder wenn ein Vertrag zur
                                  Datenverarbeitung besteht und die Datenverarbeitung mithilfe automatisierter Verfahren
                                  durchgeführt wird, steht Ihnen gegebenenfalls ein Recht auf Datenübertragbarkeit zu
                                  (Art. 20 DSGVO).
                                </li>
                              </ul>
                              <ul>
                                <li>
                                  Betroffenen steht das Recht zu, Auskunft darüber zu verlangen, ob eine automatisierte
                                  Entscheidungsfindung einschließlich Profiling besteht (Art. 22 DSGVO).
                                </li>
                              </ul>
                              <ul>
                                <li>
                                  Betroffene haben das Recht, aus Gründen, die sich aus ihrer besonderen Situation
                                  ergeben, jederzeit gegen die Verarbeitung ihrer Daten Widerspruch einzulegen, wenn die
                                  Verarbeitung ausschließlich auf Grundlage des Art. 6 Abs. 1 UAbs. 1 lit. e oder f
                                  DSGVO erfolgt (Art. 21 Abs. 1 Satz 1 DSGVO).
                                </li>
                              </ul>
                              <p>
                                <br />Sollte von den oben genannten Rechten Gebrauch gemacht werden, prüft die
                                öffentliche Stelle, ob die gesetzlichen Voraussetzungen hierfür erfüllt sind.<br /><br />Weiterhin
                                besteht ein Beschwerderecht bei einer Aufsichtsbehörde. Die für die Technische
                                Hochschule Nürnberg Georg Simon Ohm zuständige Behörde ist der Bayerische
                                Landesbeauftragte für den Datenschutz.<br />Dieser ist unter folgenden Kontaktdaten
                                erreichbar:<br />Postanschrift:<br />Postfach 22 12 19<br />80502 München<br />Adresse:<br />Wagmüllerstraße
                                18<br />80538 München<br />Tel.: +49 (0) 89 212672 - 0<br />Fax: +49 (0) 89 212672 -
                                50<br />E-Mail: poststelle@datenschutz-bayern.de<br />Internet:
                                <a
                                  @click="matomo_clicktracking('click_link', $event.target.href)"
                                  href="https://www.datenschutz-bayern.de/"
                                  target="_blank"
                                  >www.datenschutz-bayern.de</a
                                ><br /><br />
                              </p>
                              <h4>9. Sonstiges zu unserer Datenschutzerklärung</h4>
                              <p>
                                Die Technische Hochschule Nürnberg Georg Simon Ohm behält sich vor, diese
                                Datenschutzerklärung gelegentlich anzupassen, damit diese stets den aktuellen
                                rechtlichen Anforderungen entspricht oder um Änderungen der Leistungen in der
                                Datenschutzerklärung umzusetzen, z. B. bei der Einführung neuer Services. Für einen
                                erneuten Besuch der Webseiten gilt dann die neue Datenschutzerklärung.<br /><br />Wir
                                kümmern uns um die Einhaltung der Datenschutzbestimmungen in allen Bereichen unserer
                                Plattformen und unserer Hochschule. Wenn Sie Fragen haben, können Sie sich auch direkt
                                an uns wenden: datenschutz@th-nuernberg.de <br />Stand: 29. März 2022
                              </p>
                            </div>
                          </div>
                        </section>
                      </div>
                    </div>
                  </div>
                  <div class="panel panel-default">
                    <div class="panel-heading" role="tab" id="tab-97260-2-heading">
                      <h4 class="panel-title">
                        <a data-toggle="collapse" data-parent="#accordion-97260" href="#tab-97260-2" class="collapsed">
                          Datenschutzhinweis für Bewerbende
                        </a>
                      </h4>
                    </div>
                    <div
                      class="panel-collapse collapse"
                      role="tabpanel"
                      aria-labelledby="tab-97260-2-heading"
                      id="tab-97260-2"
                    >
                      <div class="panel-body">
                        <section id="c97262" class="content content-text">
                          <div class="container">
                            <div class="content-inner">
                              <p>
                                Bei Bewerbungen auf ausgeschriebene Stellen der Technischen Hochschule Nürnberg Georg
                                Simon Ohm verarbeitet die Hochschule Ihre Bewerbungsdaten ausschließlich zu diesem
                                Zweck. Weitere Informationen zur Datenverarbeitung und Rechtsgrundlagen finden Sie unter
                                den
                                <a
                                  @click="matomo_clicktracking('click_link', $event.target.href)"
                                  href="/karriere-bei-uns/stellenangebote/datenschutz/"
                                  title="Opens internal link in current window"
                                  class="internal-link"
                                  >Datenschutzhinweisen zur Verarbeitung von personenbezogenen Daten im Rahmen Ihrer
                                  Bewerbung</a
                                >.
                              </p>
                            </div>
                          </div>
                        </section>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
          <section id="c69122" class="content content-text">
            <div class="container">
              <div class="content-inner">
                <p>
                  <a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="/fileadmin/global/Gelenkte_Doks/StabSt/DSB/DSB_0250_VO_Datenschutzerklaerung_Videoeinsatz_Lehre_public.pdf"
                    title="Opens internal link in current window"
                    class="download"
                    >Datenschutzerklärung für den Einsatz von Videoanlagen in der Lehre</a
                  >
                </p>
                <p>
                  Datenschutzhinweise für den Einsatz von Videokonferenzsystemen an der Hochschule:
                  <a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="/einrichtungen-gesamt/administration-und-service/zentrale-it/videokonferenzen/ms-teams/datenschutz/"
                    title="Opens internal link in current window"
                    class="internal-link"
                    >MS Teams</a
                  >;
                  <a
                    @click="matomo_clicktracking('click_link', $event.target.href)"
                    href="/einrichtungen-gesamt/administration-und-service/zentrale-it/videokonferenzen/zoom/datenschutz/"
                    title="Opens internal link in current window"
                    class="internal-link"
                    >Zoom</a
                  >
                </p>
              </div>
            </div>
          </section>
        </div>
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

matomo_trackpageview();

const {t} = useI18n({useScope: "global"});
</script>

<style scoped>
.container {
  /* Removes redundant padding and margin from the bootstrap container class */
  padding: 0;
  margin: 0;
}
</style>
