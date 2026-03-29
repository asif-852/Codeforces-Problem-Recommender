/**
 * InfoBanner — explains who the app is for and how it works.
 * Shown at the top of the page so users understand before they search.
 */
function InfoBanner() {
  return (
    <div className="info-banner" role="note" aria-label="About this app">
      <div className="info-banner__icon" aria-hidden="true">ℹ</div>
      <div className="info-banner__body">
        <p className="info-banner__heading">Who is this for?</p>
        <p className="info-banner__text">
          This app is designed for <strong>beginner to intermediate</strong> Codeforces users
          — generally those rated <strong>below 1600</strong>. If you are unrated but already
          experienced in competitive programming, the recommendations may not suit your level.
        </p>
        <p className="info-banner__text">
          Just enter your handle and the app will analyze your submission history to
          identify your weak topics, then recommend unsolved problems that match your
          current skill level.
        </p>
      </div>
    </div>
  );
}

export default InfoBanner;
