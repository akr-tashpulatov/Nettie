export type OnboardingSlide = {
  key: string;
  img_url: string;
  title: string;
  subtitle: string;
  color: "green" | "pink";
};

export const slides: OnboardingSlide[] = [
  {
    key: "step-1",
    img_url: "/onboarding/SpeakingIllus.svg",
    title: "Practice with an AI examiner",
    subtitle:
      "Answer real IELTS questions out loud. Get instant scores on fluency, vocabulary, grammar and pronunciation.",
    color: "green",
  },
  {
    key: "step-2",
    img_url: "/onboarding/WritingIllus.svg",
    title: "Write. Submit. Improve.",
    subtitle:
      "Get your essays scored against official IELTS Band Descriptors with highlighted errors and model answers.",
    color: "pink",
  },
  {
    key: "step-3",
    img_url: "/onboarding/ProgressIllus.svg",
    title: "Watch your band rise",
    subtitle:
      "Track every session, see your scores climb, and arrive at test day confident in your target band.",
    color: "green",
  },
];
