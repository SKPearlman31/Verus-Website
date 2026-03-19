<?php get_header(); ?>
<?php $t = get_template_directory_uri(); ?>

<!-- ═══════════════ HERO ═══════════════ -->
<section class="hero" id="hero">
  <div class="hero-bg"></div>
  <div class="hero-video-bg">
    <?php if (VERUS_VIDEO_URL): ?>
    <video autoplay muted loop playsinline>
      <source src="<?php echo esc_url(VERUS_VIDEO_URL); ?>" type="video/mp4">
    </video>
    <?php endif; ?>
    <div class="hero-video-overlay"></div>
  </div>
  <div class="hero-content">
    <img src="<?php echo esc_url($t); ?>/images/logo.png" alt="Verus Basketball" class="hero-logo">
    <h1 class="hero-title">VERUS</h1>
    <p class="hero-sub">True to the Athlete</p>
    <div class="hero-tagline">
      <div class="main-quote">Basketball is the building block.</div>
      <div class="keep-main">"Keep the main thing the main thing"</div>
      <div class="base-line">Everything will come from the base.</div>
    </div>
  </div>
  <div class="hero-scroll">
    <span></span>
    <small>Scroll</small>
  </div>
</section>

<!-- ═══════════════ MISSION ═══════════════ -->
<div class="section-divider"></div>
<section class="section" id="mission">
  <div class="section-header reveal">
    <div class="section-label">Who We Are</div>
    <h2 class="section-title">Mission Statement</h2>
    <div class="section-line"></div>
  </div>
  <div class="mission-content reveal">
    <p class="mission-text">
      At Verus, our mission is to adhere to our motto of "True to the Athlete" by providing
      individually tailored, full-service representation that puts the unique needs of every
      athlete first within the framework of an agency that has a comprehensive
      understanding of the industry landscape and functions like a professional sports front
      office. Guided by our core values of service, integrity and loyalty, coupled with an
      intense focus on game development, physical performance refinement,
      biomechanics improvement, recovery enhancement, game film study, advanced
      analytics and player psychology, we are committed to maximizing our clients' careers
      on and off the court while delivering unwavering personal support at every step.
    </p>
    <div class="mission-motto">— True to the Athlete —</div>
  </div>
</section>

<!-- ═══════════════ TALENT ═══════════════ -->
<div class="section-divider"></div>
<section class="section" id="talent">
  <div class="section-header reveal">
    <div class="section-label">Our Roster</div>
    <h2 class="section-title">Our Talent</h2>
    <div class="section-line"></div>
  </div>
  <div class="talent-toggle reveal">
    <button class="active" onclick="showTalent('nba')">NBA</button>
    <button onclick="showTalent('gleague')">G-League</button>
    <button onclick="showTalent('college')">College &amp; NIL</button>
    <button onclick="showTalent('intl')">International</button>
  </div>

  <!-- Roster grids — populated dynamically from data/players.json -->
  <div class="talent-grid" id="nbaRoster"></div>
  <div class="talent-grid hidden" id="gleagueRoster"></div>
  <div class="talent-grid hidden" id="collegeRoster"></div>
  <div class="talent-grid hidden" id="intlRoster">
    <div class="roster-empty reveal visible">Coming Soon</div>
  </div>
  <div class="roster-updated" id="rosterUpdated"></div>
</section>

<!-- ═══════════════ FAMILY ═══════════════ -->
<div class="section-divider"></div>
<section class="section" id="family">
  <div class="section-header reveal">
    <div class="section-label">Behind the Scenes</div>
    <h2 class="section-title">Our Family</h2>
    <div class="section-line"></div>
  </div>

  <!-- ═══ TEAM MEMBERS ═══
       To add a team member, copy a family-card block.
       Replace initials, name, role, and bio. Add an <img> in .family-avatar for photos.
  -->
      <div class="family-grid">
<div class="card-container reveal" onclick="this.classList.toggle('flipped')">
      <div class="card-inner">
        <div class="card-front">
          <div class="family-avatar"><img src="<?php echo esc_url($t); ?>/images/team/gregg-levy.png" alt="Gregg S. Levy"></div>
          <div class="family-name">Gregg S. Levy</div>
          <div class="family-role">General Counsel</div>
          <div class="flip-hint">Click to read more →</div>
        </div>
        <div class="card-back">
          <div class="card-back-header">
            <div class="card-back-avatar"><img src="<?php echo esc_url($t); ?>/images/team/gregg-levy.png" alt="Gregg S. Levy"></div>
            <div>
              <div class="card-back-name">Gregg S. Levy</div>
              <div class="card-back-role">General Counsel</div>
            </div>
          </div>
          <div class="card-back-bio">Gregg is the General Counsel of Verus Management Team, as well as a principal in the law firm of McCarthy, Lebit, Crystal &amp; Liffman Co., L.P.A., where he focuses on corporate, business and real estate law. Gregg has been recognized as one of the top lawyers in Cleveland by the National Law Journal and has received an AV rating (highest rating possible) from the Martindale-Hubbell Law Directory. In addition to his role at Verus and his practice of law, Gregg is a real estate developer, manager, owner and partner in several nationally acclaimed restaurants and medical companies with his wife Gretchen. Gregg and Gretchen are very philanthropically inclined, serving as board members and committee members for several national charities, including Flashes of Hope, Food for the Poor and MedWish.</div>
          <div class="card-back-hint">Click to flip back</div>
        </div>
      </div>
    </div>
    <div class="card-container reveal" onclick="this.classList.toggle('flipped')">
      <div class="card-inner">
        <div class="card-front">
          <div class="family-avatar"><img src="<?php echo esc_url($t); ?>/images/team/aaron-turner.png" alt="Aaron Turner"></div>
          <div class="family-name">Aaron Turner</div>
          <div class="family-role">President, Certified NBA Agent</div>
          <div class="flip-hint">Click to read more →</div>
        </div>
        <div class="card-back">
          <div class="card-back-header">
            <div class="card-back-avatar"><img src="<?php echo esc_url($t); ?>/images/team/aaron-turner.png" alt="Aaron Turner"></div>
            <div>
              <div class="card-back-name">Aaron Turner</div>
              <div class="card-back-role">President, Certified NBA Agent</div>
            </div>
          </div>
          <div class="card-back-bio">Labeled as a hybrid of business and basketball, Aaron's passion for basketball development and business led him to co-found Verus with Gregg Levy. Prior to Verus, he gained both business and consulting knowledge through his experience and relationships in the training and management world. At age 29, Aaron had his first first-round pick, Terry Rozier, who made the biggest climb in the 2015 NBA Draft to be selected 16th overall. Aaron is key in developing his clients' skills on the court, managing day-to-day client interaction and assuring all client requests are fulfilled. He is from Cleveland and has strong ties to the grassroots basketball scene of Ohio.</div>
          <div class="card-back-hint">Click to flip back</div>
        </div>
      </div>
    </div>
    <div class="card-container reveal" onclick="this.classList.toggle('flipped')">
      <div class="card-inner">
        <div class="card-front">
          <div class="family-avatar"><img src="<?php echo esc_url($t); ?>/images/team/david-itskowitch.png" alt="David Itskowitch"></div>
          <div class="family-name">David Itskowitch</div>
          <div class="family-role">Chief Operating Officer</div>
          <div class="flip-hint">Click to read more →</div>
        </div>
        <div class="card-back">
          <div class="card-back-header">
            <div class="card-back-avatar"><img src="<?php echo esc_url($t); ?>/images/team/david-itskowitch.png" alt="David Itskowitch"></div>
            <div>
              <div class="card-back-name">David Itskowitch</div>
              <div class="card-back-role">Chief Operating Officer</div>
            </div>
          </div>
          <div class="card-back-bio">David Itskowitch is a native New Yorker, graduate of the University of Wisconsin (BA Political Science '96) and NYU Stern School of Business (MBA '24) with a passion for sports. He joined Verus in September of 2025 following eight years running his own consulting company which provided services in live sports and entertainment production, large-scale operations and project management, sports programming, event marketing/promotion strategy, deal structuring and negotiations, TV and event programming, talent management as well as event coordination. Prior to that, he was the Chief Operating Officer of Boxing for Jay Z's Roc Nation Sports. Before joining Roc Nation, he worked for more than six years as the Chief Operating Officer of Los Angeles based Golden Boy Promotions, one of the world's leading and most active boxing promoters founded by Ten-Time and Six-Division World Champion Oscar De La Hoya. Preceding his tenure at Golden Boy, he was the Vice President of New York based boxing promoter DiBella Entertainment (which he co-founded) for seven years. Before that, he worked at HBO Sports for nearly four years. Over the course of his career, he has been involved with the promotion of boxing events on five continents and overseen all aspects of the organization of some of the biggest events in the history of the sport featuring the likes of Floyd Mayweather, Manny Pacquiao, Oscar De La Hoya, Canelo Alvarez, Miguel Cotto and Bernard Hopkins from venues such as Madison Square Garden, Barclays Center, The MGM Grand Garden Arena and Crypto.com Arena.</div>
          <div class="card-back-hint">Click to flip back</div>
        </div>
      </div>
    </div>
    <div class="card-container reveal" onclick="this.classList.toggle('flipped')">
      <div class="card-inner">
        <div class="card-front">
          <div class="family-avatar"><img src="<?php echo esc_url($t); ?>/images/team/marc-hsu.png" alt="Marc Hsu"></div>
          <div class="family-name">Marc Hsu</div>
          <div class="family-role">VP of Verus Basketball</div>
          <div class="flip-hint">Click to read more →</div>
        </div>
        <div class="card-back">
          <div class="card-back-header">
            <div class="card-back-avatar"><img src="<?php echo esc_url($t); ?>/images/team/marc-hsu.png" alt="Marc Hsu"></div>
            <div>
              <div class="card-back-name">Marc Hsu</div>
              <div class="card-back-role">VP of Verus Basketball</div>
            </div>
          </div>
          <div class="card-back-bio">Marc Hsu is a seasoned basketball coach with a track record of success at the collegiate level. He joined DePaul as an assistant coach in 2019 after stops at Western Kentucky, New Mexico State, CSU Bakersfield, Texas Southern, and Binghamton. Hsu played a key role in DePaul's 12-1 start in 2019-20, contributing to six Quad 1 wins. At WKU, he helped the program to 47 wins and an NIT semifinal appearance. He also played a part in NCAA Tournament berths for New Mexico State, CSU Bakersfield, and Binghamton. A Queens, N.Y., native, he holds a business degree from Cabrini College. Recently, Hsu has tremendously helped since starting with Verus as the VP of Verus Basketball in the summer of 2021.</div>
          <div class="card-back-hint">Click to flip back</div>
        </div>
      </div>
    </div>
    <div class="card-container reveal" onclick="this.classList.toggle('flipped')">
      <div class="card-inner">
        <div class="card-front">
          <div class="family-avatar"><img src="<?php echo esc_url($t); ?>/images/team/spencer-pearlman2.png" alt="Spencer Pearlman"></div>
          <div class="family-name">Spencer Pearlman</div>
          <div class="family-role">Director of Basketball Operations &amp; Analytics</div>
          <div class="flip-hint">Click to read more →</div>
        </div>
        <div class="card-back">
          <div class="card-back-header">
            <div class="card-back-avatar"><img src="<?php echo esc_url($t); ?>/images/team/spencer-pearlman2.png" alt="Spencer Pearlman"></div>
            <div>
              <div class="card-back-name">Spencer Pearlman</div>
              <div class="card-back-role">Director of Basketball Operations &amp; Analytics</div>
            </div>
          </div>
          <div class="card-back-bio">Spencer Pearlman graduated from Vanderbilt University in 2013, where he planned to walk on to the basketball team until a back injury ended that opportunity. He earned his J.D. from the Benjamin N. Cardozo School of Law, focusing on Contracts and Negotiations. At Cardozo, he served as an editor for the Journal of Conflict Resolution, authored a note analyzing the NBA and NFL Collective Bargaining Agreements, and won a winter-session negotiation competition against more than 25 teams. After law school, Spencer began sending scouting reports to NBA teams and agencies, blending video and data to evaluate hundreds of players. That work led to a scouting and analytics role with the Phoenix Suns, followed by positions at two NBA agencies before joining Verus. Following his time with the Suns and the agency world, Spencer helped build what was essentially &ldquo;Pro Football Focus for basketball&rdquo; at Sports Info Solutions&mdash;combining film study and data to create granular, objective skill evaluations at every level. The product went far beyond box-score stats like shooting, assists, and rebounding, capturing how effective players were across every facet of the game by tracking both on- and off-ball offense and defense, delivering a clearer, more complete picture of player impact. In 2023, Aaron Turner recruited Spencer from Sports Info Solutions to bring that same NBA-level, video-and-data approach to Verus&mdash;helping model the agency after NBA front offices and stay ahead of the curve. A true &ldquo;jack of all trades,&rdquo; Spencer helps keep Verus ahead by leveraging NBA-grade data, building specialized tools and programs for clients, and knowing Verus athletes inside and out. Spencer currently serves as Verus&rsquo; Director of Operations and Analytics and is also the company&rsquo;s registered NIL agent. He is focused on expanding Verus&rsquo; NIL and college departments by bringing the same meticulous, player-first approach&mdash;blending video, data, and strategy to support athletes at every stage of their careers.</div>
          <div class="card-back-hint">Click to flip back</div>
        </div>
      </div>
    </div>
    <div class="card-container reveal" onclick="this.classList.toggle('flipped')">
      <div class="card-inner">
        <div class="card-front">
          <div class="family-avatar"><img src="<?php echo esc_url($t); ?>/images/team/john-davis.png" alt="John Davis (JD)"></div>
          <div class="family-name">John Davis (JD)</div>
          <div class="family-role">Director of Player Management</div>
          <div class="flip-hint">Click to read more →</div>
        </div>
        <div class="card-back">
          <div class="card-back-header">
            <div class="card-back-avatar"><img src="<?php echo esc_url($t); ?>/images/team/john-davis.png" alt="John Davis (JD)"></div>
            <div>
              <div class="card-back-name">John Davis (JD)</div>
              <div class="card-back-role">Director of Player Management</div>
            </div>
          </div>
          <div class="card-back-bio">A Cleveland, Ohio native and 2014 graduate of Beachwood High School, John earned his degree from Furman University in 2018 and joined Verus Sports Agency shortly after, where he has spent the past seven years working in player representation and development. With hands-on experience training and mentoring more than 25+ professional athletes, his expertise lies at the intersection of high-level player development and relationship management. His approach is rooted in consistency, communication and a commitment to maximizing both on-court performance and long-term career sustainability.</div>
          <div class="card-back-hint">Click to flip back</div>
        </div>
      </div>
    </div>
    <div class="card-container reveal" onclick="this.classList.toggle('flipped')">
      <div class="card-inner">
        <div class="card-front">
          <div class="family-avatar"><img src="<?php echo esc_url($t); ?>/images/team/stephanie-davis2.png" alt="Stephanie Davis"></div>
          <div class="family-name">Stephanie Davis</div>
          <div class="family-role">Executive Administrator</div>
          <div class="flip-hint">Click to read more →</div>
        </div>
        <div class="card-back">
          <div class="card-back-header">
            <div class="card-back-avatar"><img src="<?php echo esc_url($t); ?>/images/team/stephanie-davis2.png" alt="Stephanie Davis"></div>
            <div>
              <div class="card-back-name">Stephanie Davis</div>
              <div class="card-back-role">Executive Administrator</div>
            </div>
          </div>
          <div class="card-back-bio">As the Executive Administrator / Controller, Stephanie Davis brings nearly 20 years of experience in High-Level Administration and Corporate Accounting. In her role with the Verus Team, she supports Agents and Clients alike in everything from travel planning to contract signings. From research and development; all the way to final execution, Stephanie assists and ensures that all aspects of the company run smoothly.</div>
          <div class="card-back-hint">Click to flip back</div>
        </div>
      </div>
    </div>
    <div class="card-container reveal" onclick="this.classList.toggle('flipped')">
      <div class="card-inner">
        <div class="card-front">
          <div class="family-avatar"><img src="<?php echo esc_url($t); ?>/images/team/nodirbek-(bek)-talipov.png" alt="Nodirbek (Bek) Talipov"></div>
          <div class="family-name">Nodirbek (Bek) Talipov</div>
          <div class="family-role">Certified NBA &amp; NCAA Agent</div>
          <div class="flip-hint">Click to read more →</div>
        </div>
        <div class="card-back">
          <div class="card-back-header">
            <div class="card-back-avatar"><img src="<?php echo esc_url($t); ?>/images/team/nodirbek-(bek)-talipov.png" alt="Nodirbek (Bek) Talipov"></div>
            <div>
              <div class="card-back-name">Nodirbek (Bek) Talipov</div>
              <div class="card-back-role">Certified NBA &amp; NCAA Agent</div>
            </div>
          </div>
          <div class="card-back-bio">Nodirbek (Bek) holds a Bachelors Degree in Finance and Economics from the University of Dubuque in Iowa, and a Masters Degree in Business and Finance from Webster University in St. Louis. Before starting Florida Tax Pros, Bek worked for U.S. audit, tax, and advisory services firm KPMG Barents Group, one of the largest professional services companies in the world. Recently, Bek has served as an advisor to Ernst &amp; Young, a British multinational professional services firm specializing in assisting businesses all over the world "identify and capitalize on global business opportunities." Bek has also served as Chief Financial Officer (CFO) for multiple Central Florida Corporations and currently provides tax, accounting, and wealth management services to active and retired professional athletes. Nodirbek "Bek" Talipov came to the United States as an exchange student from Uzbekistan, the former USSR. His journey is quite inspiring as he had only $700 in his pocket and a dream. He had a partial scholarship to attend a private college in Iowa. Not being content with just being a regular college student, he took twenty-one to twenty-four credits a semester while working sixty to seventy hour weeks. He eventually graduated with a Bachelor degree in 1999 and quickly applied and was accepted to graduate school in St. Louis, MO, where he would go on to obtain his M.B.A. From there he found work as a staff accountant for "Old Town Kissimmee." It is here, where he earned his stripes, proved himself and was able to obtain a sponsor to remain in the country he fell in love with. After becoming a resident and after that a citizen, he worked for such reputable firms as KPMG Barents Group and advised for Ernst &amp; Young. However, the real sign of a man is how he treats his family, and this was never more evident than the actions he took to take care of his family. He traveled to Uzbekistan and came back with his entire family eight years ago. The rewards of this accomplishment show, as his sister is now an attorney at law after graduating from Florida State University and his mother and family own and operate a restaurant in Winter Park, Florida. The success of Bek and his family is attributable to his never say no attitude and the resiliency he displays. Bek's love for football began back in Iowa where he one day dreamed that he would be involved in the sport in some way shape or form. Through this friendship and business relationship, Bek has now realized his dream of becoming a sports agent, by recently being certified with the NFLPA in September of 2014. His background in accounting and auditing and his pure passion for the pursuit of excellence will serve future clients of the firm well.</div>
          <div class="card-back-hint">Click to flip back</div>
        </div>
      </div>
    </div>
    <div class="card-container reveal" onclick="this.classList.toggle('flipped')">
      <div class="card-inner">
        <div class="card-front">
          <div class="family-avatar"><img src="<?php echo esc_url($t); ?>/images/team/kshaun-daley.png" alt="Kshaun Daley"></div>
          <div class="family-name">Kshaun Daley</div>
          <div class="family-role">Certified FIBA Agent</div>
          <div class="flip-hint">Click to read more →</div>
        </div>
        <div class="card-back">
          <div class="card-back-header">
            <div class="card-back-avatar"><img src="<?php echo esc_url($t); ?>/images/team/kshaun-daley.png" alt="Kshaun Daley"></div>
            <div>
              <div class="card-back-name">Kshaun Daley</div>
              <div class="card-back-role">Certified FIBA Agent</div>
            </div>
          </div>
          <div class="card-back-bio">Kshaun "K" Daley is an alumni of the University of West Alabama, where he played the final 2 years of his collegiate career. A sports management major, Kshaun began coaching at the AAU travel ball level. As both coach and director, he signed a Grassroots sponsorship deal with FILA at age 24 making him one of the youngest directors in America to ever do so. Soon after, joining the Atlanta Celtics on the Adidas travel circuit where he produced multiple McDonald's All Americans, as well as professional talent on both the international and NBA level. With extensive experience in both development and management, Kshaun joined our team in 2018 and became a licensed FIBA agent in 2019. Kshaun is a "players agent" with a personal approach that allows for growth and maximization of opportunity as both a personality and a player.</div>
          <div class="card-back-hint">Click to flip back</div>
        </div>
      </div>
    </div>

    <div class="card-container reveal" onclick="this.classList.toggle('flipped')">
      <div class="card-inner">
        <div class="card-front">
          <div class="family-avatar"><img src="<?php echo esc_url($t); ?>/images/team/horace-neysmith.png" alt="Horace Neysmith"></div>
          <div class="family-name">Horace Neysmith</div>
          <div class="family-role">Recruiting &amp; Player Management</div>
          <div class="flip-hint">Click to read more →</div>
        </div>
        <div class="card-back">
          <div class="card-back-header">
            <div class="card-back-avatar"><img src="<?php echo esc_url($t); ?>/images/team/horace-neysmith.png" alt="Horace Neysmith"></div>
            <div>
              <div class="card-back-name">Horace Neysmith</div>
              <div class="card-back-role">Recruiting &amp; Player Management</div>
            </div>
          </div>
          <div class="card-back-bio">A 15-year coach at the youth level, first with the Georgia Hurricanes and currently with the Atlantic Celtics, Neysmith has seen more than 70 of his former players advance to compete collegiately, some of whom have played professionally in the NBA and Europe, including K.J. McDaniels (Houston Rockets) and Jodie Meeks (Detroit Pistons). Further, another of his former athletes, MarShon Brooks played for three NBA teams and this past season competed for Emporio Armani Milano in Italy. Neysmith is a 1985 graduate of the University of Massachusetts who earned 1985 All-Atlantic 10 Conference second team honors after averaging 14.9 points and 9.1 rebounds per game as a senior. A member of the UMass 80's Team of the Decade, Neysmith also earned 1985 NABC All-District and was a member of the 1982 Atlantic 10 All-Rookie Team.</div>
          <div class="card-back-hint">Click to flip back</div>
        </div>
      </div>
    </div>

        <!-- END FAMILY — Add more card-container blocks above this line -->
  </div>
</section>

<!-- ═══════════════ EXPERTISE ═══════════════ -->
<div class="section-divider"></div>
<section class="section" id="expertise">
  <div class="section-header reveal">
    <div class="section-label">What We Do</div>
    <h2 class="section-title">Our Expertise</h2>
    <div class="section-line"></div>
  </div>

  <div class="expertise-video reveal">
    <div class="video-wrapper">
      <?php if (VERUS_VIDEO_URL): ?>
      <video controls playsinline>
        <source src="<?php echo esc_url(VERUS_VIDEO_URL); ?>" type="video/mp4">
      </video>
      <?php endif; ?>
    </div>
  </div>

  <div class="expertise-pillars">

    <!-- PILLAR 1 -->
    <div class="pillar reveal">
      <div class="pillar-header">
        <span class="pillar-number">01</span>
        <h3 class="pillar-title">Performance</h3>
        <p class="pillar-subtitle">The foundation…basketball is the building block.</p>
      </div>
      <div class="pillar-items">
        <div class="pillar-item"><div><div class="pi-name">Game Development</div><div class="pi-desc">Personalized training and skill development programs designed to elevate every facet of on-court performance.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Physical Performance & Conditioning</div><div class="pi-desc">Cutting-edge strength, conditioning, and biomechanics programs tailored to each athlete's body and playing style.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Player Nutrition</div><div class="pi-desc">Customized nutrition planning and dietary strategy to fuel peak output, accelerate recovery and sustain elite performance across the season.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Advanced Analytics & Film Study</div><div class="pi-desc">Data-driven insights, game film breakdown and trend analysis to identify advantages, refine strategy and quantify growth.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Recovery Enhancement</div><div class="pi-desc">Structured recovery protocols, cutting-edge modalities, and comprehensive rehab coordinators to keep athletes healthy, available and performing at their peak.</div></div></div>
      </div>
    </div>

    <!-- PILLAR 2 -->
    <div class="pillar reveal">
      <div class="pillar-header">
        <span class="pillar-number">02</span>
        <h3 class="pillar-title">Representation</h3>
        <p class="pillar-subtitle">Your career…maximized and protected.</p>
      </div>
      <div class="pillar-items">
        <div class="pillar-item"><div><div class="pi-name">Contract Negotiation & Cap Strategy</div><div class="pi-desc">Strategic, data-driven negotiating that maximizes value while navigating salary cap implications, trade clauses and incentive structures.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">NIL Deal Sourcing & Compliance</div><div class="pi-desc">Identifying high-value NIL opportunities, structuring partnerships and navigating the evolving landscape of NCAA rules and state law with over $15 million in NIL deals negotiated.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Overseas & G-League Placement</div><div class="pi-desc">Leveraging international network and league relationships to find the right opportunities at every career stage.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">NBA Draft & Transfer Portal Guidance</div><div class="pi-desc">Honest evaluation, strategic positioning, combine and pro day/individual team workout preparation as well as navigating the transfer portal with precision using data and film to find the perfect fit.</div></div></div>
      </div>
    </div>

    <!-- PILLAR 3 -->
    <div class="pillar reveal">
      <div class="pillar-header">
        <span class="pillar-number">03</span>
        <h3 class="pillar-title">Brand & Marketing</h3>
        <p class="pillar-subtitle">Building what the world sees.</p>
      </div>
      <div class="pillar-items">
        <div class="pillar-item"><div><div class="pi-name">Branding & Business Ventures</div><div class="pi-desc">Moving beyond one-off deals into equity partnerships, ownership stakes and long-term brand building that compounds over time.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Social Media & Content Strategy</div><div class="pi-desc">Growing an authentic digital presence that drives engagement, attracts brand partners and amplifies athlete identity.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Media Training & Public Speaking</div><div class="pi-desc">Interview skills guidance, press conference preparation and the confidence to own every room.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Community & Philanthropy</div><div class="pi-desc">Building foundations, running camps and giving back in ways that are meaningful, sustainable and true to the athlete.</div></div></div>
      </div>
    </div>

    <!-- PILLAR 4 -->
    <div class="pillar reveal">
      <div class="pillar-header">
        <span class="pillar-number">04</span>
        <h3 class="pillar-title">Mind & Wellness</h3>
        <p class="pillar-subtitle">The inner game that drives the outer game.</p>
      </div>
      <div class="pillar-items">
        <div class="pillar-item"><div><div class="pi-name">Player Psychology & Mental Performance</div><div class="pi-desc">Building resilience, focus and the championship mindset needed to compete at the highest level day in and day out.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Mental Health & Wellness Resources</div><div class="pi-desc">Access to therapists, sport psychologists and a genuine support system that is always there, not just when things go wrong.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Family Involvement & Communication</div><div class="pi-desc">Keeping parents, spouses and inner circles informed, involved and aligned at every step of the journey.</div></div></div>
      </div>
    </div>

    <!-- PILLAR 5 -->
    <div class="pillar reveal">
      <div class="pillar-header">
        <span class="pillar-number">05</span>
        <h3 class="pillar-title">Financial & Legal</h3>
        <p class="pillar-subtitle">Protecting what you've built.</p>
      </div>
      <div class="pillar-items">
        <div class="pillar-item"><div><div class="pi-name">Financial Literacy & Money Management</div><div class="pi-desc">Connecting athletes with vetted professionals for budgeting, tax strategy, financial education, investments, property, and long-term wealth building.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Wealth Management & Real Estate</div><div class="pi-desc">Connecting athletes with vetted professionals for investments, property and long-term wealth building.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Insurance & Injury Protection</div><div class="pi-desc">Assistance with loss of value insurance and second opinion medical networks.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Legal Protection & Crisis Management</div><div class="pi-desc">Having the right team in place before anything happens with proactive legal counsel and rapid-response crisis support.</div></div></div>
      </div>
    </div>

    <!-- PILLAR 6 -->
    <div class="pillar reveal">
      <div class="pillar-header">
        <span class="pillar-number">06</span>
        <h3 class="pillar-title">Career & Lifestyle</h3>
        <p class="pillar-subtitle">Life beyond the court, planned from day one.</p>
      </div>
      <div class="pillar-items">
        <div class="pillar-item"><div><div class="pi-name">Post-Career Transition Planning</div><div class="pi-desc">Coaching pipelines, broadcasting opportunities and entrepreneurship support.</div></div></div>
        <div class="pillar-item"><div><div class="pi-name">Travel & Logistics</div><div class="pi-desc">Coordinating offseason training, travel and the day-to-day logistics that keep everything running smoothly.</div></div></div>
      </div>
    </div>

  </div>
</section>

<!-- ═══════════════ CONTACT ═══════════════ -->
<div class="section-divider"></div>
<section class="section" id="contact">
  <div class="section-header reveal">
    <div class="section-label">Get in Touch</div>
    <h2 class="section-title">Contact Us</h2>
    <div class="section-line"></div>
  </div>
  <div class="contact-wrapper reveal">
    <div id="formSuccess" style="display:none;text-align:center;padding:40px">
      <div style="font-family:var(--font-display);font-size:32px;letter-spacing:3px;margin-bottom:12px">Message Sent</div>
      <p style="color:var(--gray-light)">Thank you for reaching out. We'll be in touch soon.</p>
    </div>
    <!-- IMPORTANT: Replace YOUR_EMAIL_HERE above with the actual recipient email address -->
    <form id="contactForm" action="https://formsubmit.co/admin@verusbasketball.com" method="POST">
      <!-- ═══ CONTACT EMAIL SETUP ═══
           Replace YOUR_EMAIL_HERE in the form action with your actual email address.
           FormSubmit.co will forward submissions to that email for free.
           On first submission, you'll get a confirmation email to activate.
      -->
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_template" value="table">
      <input type="hidden" name="_subject" value="Verus Basketball — New Contact Form Submission">
      <div class="form-row">
        <div class="form-group">
          <label for="name">Full Name *</label>
          <input type="text" id="name" name="name" required placeholder="Your name">
        </div>
        <div class="form-group">
          <label for="email">Email Address *</label>
          <input type="email" id="email" name="email" required placeholder="you@email.com">
        </div>
      </div>
      <div class="form-group">
        <label for="phone">Phone Number <span style="color:var(--gray)">(Optional)</span></label>
        <input type="tel" id="phone" name="phone" placeholder="(555) 000-0000">
      </div>
      <div class="form-group">
        <label for="subject">Subject *</label>
        <input type="text" id="subject" name="_subject" required placeholder="What is this regarding?">
      </div>
      <div class="form-group">
        <label for="message">Message *</label>
        <textarea id="message" name="message" required placeholder="Tell us how we can help..."></textarea>
      </div>
      <button type="submit" class="submit-btn">Send Message</button>
      <p class="form-note">We typically respond within 24–48 hours.</p>
    </form>
  </div>
</section>

<?php get_footer(); ?>
