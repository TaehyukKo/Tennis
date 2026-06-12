import random
from collections import defaultdict
from itertools import combinations


class Scheduler:


    def __init__(
        self,
        teamA_men,
        teamB_men,
        teamA_women,
        teamB_women,
        courts,
        rounds,
        min_games
    ):

        self.courts = courts
        self.rounds = rounds
        self.min_games = min_games

        self.AM = teamA_men
        self.BM = teamB_men

        self.AW = teamA_women
        self.BW = teamB_women

        self.players = (
            self.AM + self.BM +
            self.AW + self.BW
        )


    def generate(self, retry=10000):

        for _ in range(retry):

            result = self._try_generate()

            if result:
                return result

        raise Exception("생성 실패")

    def _try_generate(self):

        play_count = defaultdict(int)

        history = {
            p: [False] * self.rounds
            for p in self.players
        }

        partner_count = defaultdict(int)
        opponent_count = defaultdict(int)

        schedule = []

        for r in range(self.rounds):

            used = set()
            round_matches = []

            for c in range(self.courts):

                match_type = random.choice(
                    ["남복", "여복", "혼복"]
                )

                match = self.make_match(
                    match_type,
                    used,
                    r,
                    history,
                    play_count,
                    partner_count,
                    opponent_count
                )

                if match is None:
                    return None

                a_pair, b_pair = match

                players = a_pair + b_pair

                for p in players:
                    used.add(p)
                    play_count[p] += 1
                    history[p][r] = True

                self.record_partner(
                    a_pair,
                    partner_count
                )
                self.record_partner(
                    b_pair,
                    partner_count
                )

                self.record_opponents(
                    a_pair,
                    b_pair,
                    opponent_count
                )

                round_matches.append({
                    "court": c + 1,
                    "type": match_type,
                    "A": a_pair,
                    "B": b_pair
                })

            schedule.append(round_matches)

        if min(play_count.values()) < self.min_games:
            return None

        return schedule, play_count

    def can_play(self, player, r, history):

        if r < 2:
            return True

        return not (
            history[player][r-1]
            and history[player][r-2]
        )

    def pair_score(
        self,
        pair,
        partner_count,
        play_count
    ):

        p1, p2 = pair

        return (
            partner_count[tuple(sorted(pair))] * 100
            + play_count[p1]
            + play_count[p2]
        )

    def make_match(
        self,
        match_type,
        used,
        r,
        history,
        play_count,
        partner_count,
        opponent_count
    ):

        if match_type == "남복":

            A = [
                p for p in self.AM
                if p not in used
                and self.can_play(
                    p,
                    r,
                    history
                )
            ]

            B = [
                p for p in self.BM
                if p not in used
                and self.can_play(
                    p,
                    r,
                    history
                )
            ]

            if len(A) < 2 or len(B) < 2:
                return None

            a_pair = min(
                combinations(A, 2),
                key=lambda x:
                self.pair_score(
                    x,
                    partner_count,
                    play_count
                )
            )

            b_pair = min(
                combinations(B, 2),
                key=lambda x:
                self.pair_score(
                    x,
                    partner_count,
                    play_count
                )
            )

            return list(a_pair), list(b_pair)

        if match_type == "여복":

            A = [
                p for p in self.AW
                if p not in used
                and self.can_play(
                    p,
                    r,
                    history
                )
            ]

            B = [
                p for p in self.BW
                if p not in used
                and self.can_play(
                    p,
                    r,
                    history
                )
            ]

            if len(A) < 2 or len(B) < 2:
                return None

            a_pair = min(
                combinations(A, 2),
                key=lambda x:
                self.pair_score(
                    x,
                    partner_count,
                    play_count
                )
            )

            b_pair = min(
                combinations(B, 2),
                key=lambda x:
                self.pair_score(
                    x,
                    partner_count,
                    play_count
                )
            )

            return list(a_pair), list(b_pair)

        # 혼복

        AM = [
            p for p in self.AM
            if p not in used
            and self.can_play(
                p,
                r,
                history
            )
        ]

        AW = [
            p for p in self.AW
            if p not in used
            and self.can_play(
                p,
                r,
                history
            )
        ]

        BM = [
            p for p in self.BM
            if p not in used
            and self.can_play(
                p,
                r,
                history
            )
        ]

        BW = [
            p for p in self.BW
            if p not in used
            and self.can_play(
                p,
                r,
                history
            )
        ]

        if not AM or not AW or not BM or not BW:
            return None

        a_m = min(AM, key=lambda x: play_count[x])
        a_w = min(AW, key=lambda x: play_count[x])

        b_m = min(BM, key=lambda x: play_count[x])
        b_w = min(BW, key=lambda x: play_count[x])

        return [a_m, a_w], [b_m, b_w]

    def record_partner(
        self,
        pair,
        partner_count
    ):
        partner_count[
            tuple(sorted(pair))
        ] += 1

    def record_opponents(
        self,
        a_pair,
        b_pair,
        opponent_count
    ):

        for a in a_pair:
            for b in b_pair:

                key = tuple(sorted([a, b]))
                opponent_count[key] += 1


def kakao_format(schedule):

    text = "🎾 복식 대진표\n\n"

    for r, matches in enumerate(
        schedule,
        start=1
    ):

        text += f"[{r}라운드]\n\n"

        for m in matches:

            a = "+".join(m["A"])
            b = "+".join(m["B"])

            text += (
                f"코트{m['court']} "
                f"({m['type']})\n"
                f"{a}  vs  {b}\n\n"
            )

    return text


# 사용 예시
sch = Scheduler(
    teamA_men=["김철수", "이영희", "박민수", "정우성", "홍길동", "강백호"],
    teamB_men=["최민준", "오세훈", "윤성호", "김동현", "박지성", "손흥민"],
    teamA_women=["김민지", "박수진", "이지은", "최유나"],
    teamB_women=["한지민", "송혜교", "김태희", "전지현"],
    courts=2,
    rounds=10,
    min_games=3
)

schedule, counts = sch.generate()

print(kakao_format(schedule))
