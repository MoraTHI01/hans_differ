<template>
  <HeaderRow />
  <LogoAndSearchbarRow :placeholder="t('LegalView.searchplaceholder')" :showSearch="false" :showProgress="false" />
  <div class="main-container">
    <MenuBanner :menutext="t('LegalView.menutext')" />
    <div v-if="$i18n.locale === 'en'" class="sub-container container">
      <div class="content-inner">
        <p><strong>Publisher</strong></p>
        <p>
          The website of the Hochschul Assistenz System (HAnS) research prototype is not part of the official website of
          Nuremberg Institute of Technology. The website is published as a research prototype in the HAnS collaborative
          project.
        </p>
        <p><strong>Address</strong></p>
        <p>
          Verbundprojekt HAnS<br />
          Technische Hochschule Nürnberg Georg Simon Ohm<br />
          Kesslerplatz 12<br />
          90489 Nürnberg<br />
          Tel. +49 (0)911 -5880-1632<br />
          Email:
          <a
            @click="matomo_clicktracking('click_link', $event.target.href)"
            href="mailto:verbundprojekt-hans@th-nuernberg.de"
            >verbundprojekt-hans<span class="fa fa-at"><span class="sr-only">at</span></span
            >th-nuernberg<span class="fa fa-circle dot-subst"><span class="sr-only">Dot</span></span
            >de</a
          ><br />
          Website:
          <a
            @click="matomo_clicktracking('click_link', $event.target.href)"
            href="http://hans.th-nuernberg.de"
            target="_blank"
            >hans.th-nuernberg.de</a
          >
        </p>
        <p>&nbsp;</p>
        <p><strong>Contact person for content issues</strong></p>
        <p>
          Verbundprojekt HAnS Tech Team<br />
          Technische Hochschule Nürnberg Georg Simon Ohm<br />
          Kesslerplatz 12<br />
          90489 Nuremberg<br />
          Email:
          <a
            @click="matomo_clicktracking('click_link', $event.target.href)"
            href="mailto:tobias.bocklet@th-nuernberg.de, korbinian.riedhammer@th-nuernberg.de,
            thomas.ranzenberger@th-nuernberg.de,fabian.schneider@th-nuernberg.de,christopher.simic@th-nuernberg.de"
            title="Opens internal link in current window"
            class="mail"
            >HAnSTechTeam<span class="fa fa-at"><span class="sr-only">at</span></span
            >th-nuernberg<span class="fa fa-circle dot-subst"><span class="sr-only">Dot</span></span
            >de</a
          >
        </p>
        <p><strong>Responsible supervisory authority</strong></p>
        <p>
          PT Digitale Hochschulbildung<br />
          VDI/VDE Innovation + Technik GmbH<br />
          Steinplatz 1<br />
          10623 Berlin<br />
          Website:&nbsp;<a
            @click="matomo_clicktracking('click_link', $event.target.href)"
            href="https://vdivde-it.de/de"
            title="Opens internal link in current window"
            target="_blank"
            class="external-link-new-window"
            >www.vdivde-it.de</a
          >
        </p>
        <p><strong>VAT number</strong></p>
        <p>DE 222 858 358 (according to Section 27a VAT Act [Umsatzsteuergesetz])</p>
        <p><strong>Conditions of use</strong></p>
        <p>Texts, images, graphics and the layout of this website may be subject to copyright law.</p>
        <p>According to Section 5 of the German Copyright Law [UrhG], the following are not subject to copyright:</p>
        <p>
          laws, regulations, official decrees and notifications, decisions and official guidelines on decisions and
          other official works which have been published in the official interest for general knowledge, with the
          restriction that the provisions concerning prohibition of change and citing of sources in Section 62 paras 1
          to 3 and Section 63 paras 1 and 2 UrhG must be applied accordingly.
        </p>
        <p>
          As a private individual, you are allowed to use material protected by copyright law for private and other
          personal use within the framework of
          <a
            @click="matomo_clicktracking('click_link', $event.target.href)"
            href="http://www.gesetze-im-internet.de/urhg/__53.html"
            target="_self"
            >Section 53 UrhG </a
          >. Reproduction or use of material protected by copyright law in these pages or parts of it in other
          electronic or printed publications and publishing of them is only permitted with our consent. Consent is
          granted on request by the persons responsible for the content. Reprinting and evaluation of press releases and
          speeches are generally permitted, as long as the source is cited.
        </p>
        <p>
          Furthermore, texts, images, graphics and other files may be completely or partially subject to third-party
          copyright. The persons responsible for the content can also give you further information about the existence
          of possible third-party rights.
        </p>
        <p><strong>Exclusion of liability</strong></p>
        <p>
          The content of this website and the information provided have been carefully researched, and edited and
          checked to the best of our knowledge and belief. They are verified, corrected, supplemented and updated at
          regular intervals.&nbsp; Nevertheless, Nuremberg Institute of Technology cannot guarantee the (up-to-date)
          accuracy, completeness, legal certainty, quality or availability at all times of the information provided.
        </p>
        <p>
          It accepts no liability for losses or any other consequences that arise as a result of direct or indirect use
          or non-use of the information provided on the website of Nuremberg Institute of Technology. The exclusion of
          liability shall not apply in so far as the provisions of Section 839 of the German Civil Code (liability in
          the event of a breach of official duty) apply. No liability can be accepted for any losses that occur as a
          result of the call-up or downloading of data by computer viruses, spoofing software or other malware or as a
          result of installing or using software or data.<br />
          Webpages or content labelled by name shall be deemed to represent the opinions and expertise of the authors.
        </p>
        <p>
          As a service provider, we are responsible for our own contents on these pages according to Section 7 para 1
          TMG (German Telemedia Act) in accordance with general law. According to Sections 8 to 10 TMG, however, as a
          service provider, we are not obliged to monitor transmitted or stored third-party information or to research
          circumstances which indicate illegal activity. Obligations to remove or block the use of information according
          to general law remain unaffected by this. However, liability in this connection only applies after knowledge
          has been acquired of a specific infringement of law. On learning of such legal infringements, we will
          immediately remove this content.
        </p>
        <p>
          Nuremberg Institute of Technology expressly reserves the right to amend, add to or delete individual webpages
          or the entire website without special announcement or to temporarily or permanently discontinue its
          publication.
        </p>
        <p><strong>Links</strong></p>
        <p>
          Our own content should be considered distinct from cross-references (links) to other providers’ websites.
          These links only enable access for the use of third-party content according to Section 8 of the Telemedia Act.
          When linking to these internet contents for the first time, we checked these third-party contents as to
          whether they could entail possible civil or criminal liability. However, we cannot constantly check
          third-party content for changes and can therefore accept no responsibility for it. The provider of the website
          shall be exclusively liable with regard to illegal, erroneous or incomplete content, and particularly with
          regard to losses arising as a result of the use or non-use of third-party information.
        </p>
        <p><strong>Copyright</strong></p>
        <p>
          Reproduction and reuse of texts and graphics requires the permission of Nuremberg Institute of Technology.
          Please also note that images, graphics, text or other files are subject to third-party copyright in whole or
          in part.
        </p>
        <p><strong>Legal force of the provisions above</strong></p>
        <p>
          The provisions above, particularly the liability and guarantee exclusions provided for above, shall apply to
          all websites operated by Nuremberg Institute of Technology unless stated otherwise, and shall be regarded as
          part of the website that makes reference to this page. In so far as any one or more regulations in the
          provisions above no longer comply (in full) with applicable law, this shall not affect the content or the
          validity of the remaining regulations in the provisions above.
        </p>
        <p><strong>Competent court</strong></p>
        <p>Any legal disputes arising in relation to this website shall be exclusively subject to German law.</p>
        <p><em>Amended: 08 June 2020</em></p>
      </div>
    </div>
    <div v-else class="container">
      <div class="content-inner">
        <h2>Impressum</h2>
        <p><strong>Herausgeber</strong></p>
        <p>
          Die Website des Forschungsprototyps Hochschul Assistenz System (HAnS) ist nicht Teil der offiziellen Website
          der Technischen Hochschule Nürnberg. Die Website wird als Forschungsprototyp im Rahmen des
          HAnS-Verbundprojekts veröffentlicht.
        </p>
        <p><strong>Anschrift</strong></p>
        <p>
          Verbundprojekt HAnS<br />
          Technische Hochschule Nürnberg Georg Simon Ohm<br />
          Kesslerplatz 12<br />
          90489 Nürnberg<br />
          Tel. +49 (0)911 -5880-1632<br />
          Email:
          <a
            @click="matomo_clicktracking('click_link', $event.target.href)"
            href="mailto:verbundprojekt-hans@th-nuernberg.de"
            >verbundprojekt-hans<span class="fa fa-at"><span class="sr-only">at</span></span
            >th-nuernberg<span class="fa fa-circle dot-subst"><span class="sr-only">Dot</span></span
            >de</a
          ><br />
          Website:
          <a
            @click="matomo_clicktracking('click_link', $event.target.href)"
            href="http://hans.th-nuernberg.de"
            target="_blank"
            >hans.th-nuernberg.de</a
          >
        </p>
        <p><strong>Kontaktperson für den Inhalt</strong></p>
        <p>
          Webredaktion der Hochschulkommunikation der TH Nürnberg<br />Fax 0911-5880-8222<br />
          E-Mail:
          <a
            @click="matomo_clicktracking('click_link', $event.target.href)"
            href="mailto:presse@th-nuernberg.de"
            title="Opens internal link in current window"
            class="mail"
            >presse<span class="fa fa-at"><span class="sr-only">at</span></span
            >th-nuernberg<span class="fa fa-circle dot-subst"><span class="sr-only">Punkt</span></span
            >de</a
          >
        </p>
        <p>
          Redaktionell verantwortlich für die Einzelthemen sind die auf den einzelnen Informationsseiten genannten
          Ansprechpartner*innen oder Einrichtungen der TH Nürnberg. Die redaktionelle Bearbeitung der Inhalte erfolgt
          durch die jeweils zuständigen Fakultäten und Einrichtungen der TH Nürnberg.
        </p>
        <p><strong>Zuständige Aufsichtsbehörde</strong></p>
        <p>
          PT Digitale Hochschulbildung<br />
          VDI/VDE Innovation + Technik GmbH<br />
          Steinplatz 1<br />
          10623 Berlin<br />
          Website:&nbsp;<a
            @click="matomo_clicktracking('click_link', $event.target.href)"
            href="https://vdivde-it.de/de"
            title="Opens internal link in current window"
            target="_blank"
            class="external-link-new-window"
            >www.vdivde-it.de</a
          >
        </p>
        <p><strong>Umsatzsteueridentifikationsnummer</strong></p>
        <p>DE 222 858 358 (gemäß § 27a Umsatzsteuergesetz)</p>
        <p><strong>Nutzungsbedingungen</strong></p>
        <p>Texte, Bilder, Grafiken sowie die Gestaltung dieser Internetseiten können dem Urheberrecht unterliegen.</p>
        <p>Nicht urheberrechtlich geschützt sind nach § 5 des Urheberrechtsgesetzes (UrhG)</p>
        <p>
          Gesetze, Verordnungen, amtliche Erlasse und Bekanntmachungen sowie Entscheidungen und amtlich verfasste
          Leitsätze zu Entscheidungen und andere amtliche Werke, die im amtlichen Interesse zur allgemeinen
          Kenntnisnahme veröffentlicht worden sind, mit der Einschränkung, dass die Bestimmungen über Änderungsverbot
          und Quellenangabe in § 62 Abs. 1 bis 3 und § 63 Abs. 1 und 2 UrhG entsprechend anzuwenden sind.
        </p>
        <p>
          Als Privatperson dürfen Sie urheberrechtlich geschütztes Material zum privaten und sonstigen eigenen Gebrauch
          im Rahmen des&nbsp;
          <a
            @click="matomo_clicktracking('click_link', $event.target.href)"
            href="http://www.gesetze-im-internet.de/urhg/__53.html"
            target="_self"
            >§ 53 Urheberrechtsgesetz (UrhG) </a
          >&nbsp; verwenden. Eine Vervielfältigung oder Verwendung urheberrechtlich geschützten Materials dieser Seiten
          oder Teilen davon in anderen elektronischen oder gedruckten Publikationen und deren Veröffentlichung ist nur
          mit unserer Einwilligung gestattet. Diese erteilen auf Anfrage die für den Inhalt Verantwortlichen. Der
          Nachdruck und die Auswertung von Pressemitteilungen und Reden sind mit Quellenangabe allgemein gestattet.
        </p>
        <p>
          Weiterhin können Texte, Bilder, Grafiken und sonstige Dateien ganz oder teilweise dem Urheberrecht Dritter
          unterliegen. Auch über das Bestehen möglicher Rechte Dritter geben Ihnen die für den Inhalt Verantwortlichen
          nähere Auskünfte.
        </p>
        <p><strong>Haftungsausschluss</strong></p>
        <p>
          Die Inhalte dieses Internetangebotes und die bereitgestellten Informationen sind sorgfältig recherchiert und
          nach bestem Wissen und Gewissen erarbeitet und geprüft. In regelmäßigen Abständen werden sie überprüft,
          berichtigt, ergänzt und aktualisiert.&nbsp; Dennoch kann die Technische Hochschule Nürnberg Georg Simon Ohm
          keine Gewähr für die Aktualität, Richtigkeit, Vollständigkeit, rechtliche Unbedenklichkeit, Qualität und
          jederzeitige Verfügbarkeit der bereitgestellten Informationen übernehmen.
        </p>
        <p>
          Es wird nicht gehaftet für Schäden oder sonstige Konsequenzen, die durch die direkte oder indirekte Nutzung
          oder Nichtnutzung der im Internetangebot der Technischen Hochschule Nürnberg Georg Simon Ohm angebotenen
          Informationen entstehen. Der Haftungsausschluss gilt nicht, soweit die Vorschriften des § 839 BGB (Haftung bei
          Amtspflichtverletzung) einschlägig sind. Für etwaige Schäden, die beim Aufrufen oder Herunterladen von Daten
          durch Computerviren, Manipulations- oder sonstige Schadsoftware oder bei der Installation oder Nutzung von
          Software oder Daten verursacht werden, wird nicht gehaftet.<br />
          Namentlich gekennzeichnete Internetseiten oder Inhalte geben die Auffassungen und Erkenntnisse der abfassenden
          Personen wieder.
        </p>
        <p>
          Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen
          Gesetzen verantwortlich. Nach § 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht verpflichtet,
          übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf
          eine rechtswidrige Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von
          Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch
          erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden von
          entsprechenden Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.
        </p>
        <p>
          Die Technische Hochschule Nürnberg Georg Simon Ohm behält es sich ausdrücklich vor, einzelne Webseiten oder
          das gesamte Internetangebot ohne gesonderte Ankündigung zu verändern, zu ergänzen, zu löschen oder die
          Veröffentlichung zeitweise oder endgültig einzustellen.
        </p>
        <p><strong>Links</strong></p>
        <p>
          Von unseren eigenen Inhalten sind Querverweise („Links“) auf die Webseiten anderer Anbieter zu unterscheiden.
          Durch diese Links ermöglichen wir lediglich den Zugang zur Nutzung fremder Inhalte nach § 8 Telemediengesetz.
          Bei der erstmaligen Verknüpfung mit diesen Internetangeboten haben wir diese fremden Inhalte daraufhin
          überprüft, ob durch sie eine mögliche zivilrechtliche oder strafrechtliche Verantwortlichkeit ausgelöst wird.
          Wir können diese fremden Inhalte aber nicht ständig auf Veränderungen überprüfen und daher auch keine
          Verantwortung dafür übernehmen. Für illegale, fehlerhafte oder unvollständige Inhalte und insbesondere für
          Schäden, die aus der Nutzung oder Nichtnutzung von Informationen Dritter entstehen, haftet allein der
          jeweilige Anbieter der Seite.
        </p>
        <p><strong>Urheberrecht / Copyright</strong></p>
        <p>
          Die Kopie und die Weiterverwendung von Text und Graphik erfordert die Zustimmung der Technischen Hochschule
          Nürnberg Georg Simon Ohm. Zudem gilt zu beachten, dass Bilder, Graphiken, Text- oder sonstige Dateien ganz
          oder teilweise dem Urheberrecht Dritter unterliegen.
        </p>
        <p><strong>Rechtswirksamkeit der vorstehenden Bestimmungen</strong></p>
        <p>
          Die vorstehenden Bestimmungen, insb. die vorstehend bestimmten Haftungs- und Gewährleistungsausschlüsse,
          gelten, soweit nicht ein anderes bestimmt ist, für jedes von der Technischen Hochschule Nürnberg Georg Simon
          Ohm betriebene Internetangebot und sind als Teil des Internetangebotes zu betrachten, von dem aus auf diese
          Seite verwiesen wurde. Sofern einzelne oder mehrere Regelungen der vorstehenden Bestimmungen der geltenden
          Rechtslage nicht, nicht mehr oder nicht vollständig entsprechen sollten, bleiben die übrigen Regelungen der
          vorstehenden Bestimmungen in ihrem Inhalt und ihrer Gültigkeit davon unberührt.
        </p>
        <p><strong>Gerichtsstand</strong></p>
        <p>Alle aus dieser Website entstehenden Rechtsstreitigkeiten unterliegen ausschließlich deutschem Recht.</p>
        <p><em>Geändert: 24. November 2020</em></p>
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
const {t} = useI18n({useScope: "global"});
matomo_trackpageview();
</script>

<style scoped>
.container {
  /* Removes redundant padding and margin from the bootstrap container class */
  padding: 0;
  margin: 0;
}
</style>
