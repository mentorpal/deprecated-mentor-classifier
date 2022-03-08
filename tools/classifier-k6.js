import http from "k6/http";
import { SharedArray } from "k6/data";
import { check } from "k6";

const apiUrl = 'https://careerfair.mentorpal.org/classifier/questions/?referer=load-test'
const questions = new SharedArray("user questions", function () {
  return JSON.parse(open("./questions.json"));
});
const mentors = [
  "610dad8c16e879e3c3c6f711",
  "610dd3f616e879e3c3d88818",
  "610e854f16e879e3c32ea550",
  "610e860416e879e3c32efbd4",
  "61294d8a54f80968440320df",
  "612e636c54f80968446cb57c",
  "614394d406c21f1afa434db7",
  "614398e306c21f1afa459f56",
  "6144bc7d06c21f1afaeb59a4",
  "6153ae754be7d1a8ecc1e8f3",
  "6171b620c7ea4df5a68702db",
  "61796622c7ea4df5a61febd1",
  "61843084c7ea4df5a62c6f21",
  "619c22d3836e4af90c8fc131",
  "61b20a97836e4af90c0df4b6",
  "61ba2ef59e733a8a0eb8c3dd",
  "61c2435f9e733a8a0e25ce1b",
];
export default function () {
  // randomly pick one mentor and question:
  const q = questions[Math.floor(Math.random() * questions.length)];
  const m = mentors[Math.floor(Math.random() * mentors.length)];
  const url = `${apiUrl}&mentor=${m}&query=${q}`; // q is already encoded
  const req = http.get(url.toString(), { tags: { name: "ask" } });

  check(req, {
    "is status 200": (r) => r.status === 200,
  });
  if (req.status === 200) {
    const res = req.json();
    // console.log(res.answer_text, q)
    check(res, {
      "has no errors": (r) => "errors" in r === false,
      //	    'has an answer': (r) => r.answer_text && r.answer_text.length > 2,
    });
  } else {
    console.log(req.status, req.text, req.body, m, q);
    console.log(url.toString());
  }
}
