""" Bid for Game
    Acol AdvancersBid module
"""

import inspect
from .bridge_tools import Bid, Pass, Double
from .bidding_hand import BiddingHand

# uncomment line around 30 for generating compliance tests. Affects hand 361!!!


class AdvancersBid(BiddingHand):
    """BfG AdvancersBid class."""
    def __init__(self, hand_cards, board):
        super(AdvancersBid, self).__init__(hand_cards, board)
        self.trace = 0

    def suggested_bid(self):
        """Direct control to relevant method and return a Bid object."""
        if self._overcall_bid_at_three_level():
            bid = self._respond_to_three_level()
        elif self.overcaller_bid_one.is_double:
            bid = self._overcaller_has_doubled()
        elif (self.shape[0] >= 9 and
                # comment when not running immersion test
                # self.longest_suit not in self.opponents_suits and
                #
                self.next_level(self.longest_suit) <= 4):
            bid = self.suit_bid(4, self.longest_suit, '0592')
        elif self._has_biddable_eight_card_suit():
            bid = self.bid_to_game(self.longest_suit, '0040')
        elif self.overcaller_bid_one.is_nt:
            bid = self._respond_to_nt()
        elif self._has_three_card_support_for_overcallers_major():
            bid = self._support_for_overcaller()
        elif self._is_weak_no_support_for_overcaller():
            bid = self.nt_bid(1, '0103')
        elif self._has_biddable_suit():
            bid = self._long_suit_bid()
        elif self._can_bid_nt_opposition_has_no_fit():
            bid = self._no_support_stoppers()
        elif self._can_support_overcaller():
            bid = self._support_for_overcaller()
        elif self._has_opening_values_can_bid_nt():
            bid = self._bid_nt()
        elif self.hcp >= 12:
            bid = self._long_suit_bid()
        else:
            bid = Pass('0593')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _respond_to_three_level(self):
        """Respond to 3 level bid."""
        jump_bid = self.is_jump(self.opener_bid_one, self.overcaller_bid_one)
        if self.overcaller_bid_one.is_game:
            bid = Pass('0596')
        elif self._can_bid_six_card_suit_at_three_level():
            bid = self.next_level_bid(self.longest_suit, '0882')
        elif self._has_ten_points_and_stoppers():
            bid = self.nt_bid(3, '0597')
        elif self._can_bid_to_game(self.overcaller_bid_one.denomination):
            bid = self.bid_to_game(self.overcaller_bid_one.denomination, '0598')
        elif self.hcp >= 10 and self.suit_length(self.overcaller_bid_one.denomination) >= 4:
            bid = self.next_level_bid(self.overcaller_bid_one.denomination, '0305')
        elif self.hcp >= 7 and self.opener_bid_one.level >= 2 and not jump_bid:
            bid = Pass('0599')
        elif self._has_eight_points_and_stoppers():
            bid = self.nt_bid(3, '0601')
        else:
            bid = Pass('0602')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _overcaller_has_doubled(self):
        """Bid after partner has doubled."""
        if self._has_eleven_points_balanced_and_responder_has_bid_game():
            bid = Double('0603')
        elif self._is_weak_and_intervening_bid():
            bid = Pass('0604')
        elif self.opener_bid_one.name == '1NT':
            bid = self._overcaller_doubled_one_nt()
        else:
            bid = self._overcaller_has_doubled_weak()
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _overcaller_doubled_one_nt(self):
        """Bid after overcaller has doubled opener's 1NT."""
        if 4 <= self.hcp <= 7:
            bid = self._long_suit_bid()
        elif not self.responder_bid_one.is_pass:
            bid = self._overcaller_doubled_one_nt_responder_bid()
        elif self.five_card_suit_or_better and self.hcp <= 4:
            suit = self.longest_suit
            bid = self.next_level_bid(suit, '0605')
        else:
            bid = Pass('0606')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _overcaller_doubled_one_nt_responder_bid(self):
        """Bid after overcaller has doubled opener's 1NT, responder has bid."""
        if self.is_semi_balanced and self.stoppers_in_bid_suits:
            bid = self._semi_balanced_stoppers()
        else:
            bid = self._long_suit_bid()
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _semi_balanced_stoppers(self):
        """Return bid if semi-balanced with stoppers in bid suits."""
        if self.hcp <= 9 and self.nt_level <= 2:
            bid = self.nt_bid(2, '0607')
        elif self.nt_level <= 3:
            bid = self.nt_bid(3, '0608')
        else:
            bid = self._long_suit_bid()
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _overcaller_has_doubled_weak(self):
        """Bid after partner has doubled with a weak hand."""
        if self._weak_and_responder_has_bid():
            bid = Pass('0609')
        elif self._leave_double():
            bid = Pass('0610')
        elif self.is_balanced and self.stoppers_in_bid_suits:
            bid = self._overcaller_has_doubled_weak_balanced()
        else:
            bid = self._long_suit_bid()
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _overcaller_has_doubled_weak_balanced(self):
        """Bid after partner has doubled with a weak balanced hand."""
        major_suit = self._find_four_card_major()
        if self.opponents_at_game:
            bid = Pass('0904')
        elif self.hcp <= 5:
            bid = self._long_suit_bid()
        elif major_suit:
            raise_level = self._find_level_for_major_raise(major_suit)
            bid = self.next_level_bid(major_suit, '0611', raise_level)
        elif self.opener_bid_one.level == 2 and self.nt_level <= 2:
            bid = self.nt_bid(2, '0612')
        elif self._has_ten_points_and_opening_bid_is_weak_three():
            bid = self.nt_bid(3, '0613')
        elif self.hcp >= 12 and self.nt_level <= 3:
            bid = self.nt_bid(3, '0614')
        elif self.hcp >= 10 and self.nt_level <= 2:
            bid = self.nt_bid(2, '0615')
        elif self.hcp >= 6 and self.nt_level <= 1:
            bid = self.nt_bid(1, '0616')
        else:
            bid = self._long_suit_bid()
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _support_for_overcaller(self):
        """Returns bid in partner's suit relevant to points."""
        if self._has_thirteen_points_and_five_card_major():
            bid = self._long_suit_bid()
        elif self.overcaller_bid_one.level == 1:
            bid = self._support_for_overcaller_level_one()
        elif self.overcaller_bid_one.level == 2:
            bid = self._support_for_overcaller_level_two()
        elif self.hcp >= 12 and not self.bidding_above_game:
            bid = self.next_level_bid(self.overcaller_bid_one.denomination, '0888')
        elif self._has_strength_and_support_for_overcallers_three_level_bid():
            bid = self.next_level_bid(self.overcaller_bid_one.denomination, '0565')
        else:
            bid = Pass('0617', True)
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _support_for_overcaller_level_one(self):
        """Returns bid in partner's suit after level one bid."""
        suit_to_bid = self.overcaller_bid_one.denomination
        if self._has_ten_points_overcaller_bid_minor():
            bid = self._bid_nt()
        elif self._can_support_overcaller_at_given_level(level=2):
            bid = self.suit_bid(2, suit_to_bid, '0618', True)
        elif self._can_support_overcaller_at_given_level(level=3):
            bid = self.suit_bid(3, suit_to_bid, '0619', True)
        elif self._can_support_overcaller_at_given_level(level=4):
            bid = self.suit_bid(4, suit_to_bid, '0620', True)
        else:
            bid = Pass('0621', True)
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _bid_nt(self):
        """Return a NT bid."""
        if self.hcp >= 13 and self.nt_level <= 3:
            bid = self.nt_bid(3, '0622')
        elif self.hcp >= 12 and self.nt_level <= 2:
            bid = self.nt_bid(2, '0623')
        elif self.nt_level <= 1:
            bid = self.nt_bid(1, '0624')
        else:
            bid = Pass('0625')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _support_for_overcaller_level_two(self):
        """Returns bid in partner's suit after level two bid."""
        suit_to_bid = self.overcaller_bid_one.denomination
        hand_value_points = self._get_hand_value_points(suit_to_bid)
        bid_level = self.next_level(suit_to_bid)
        if self._opening_hand_and_overcaller_bid_minor():
            bid = self.nt_bid(3, '0626')
        elif self._ten_points_and_overcaller_bid_minor():
            bid = self.nt_bid(2, '0627')
        elif hand_value_points in range(9, 14) and bid_level <= 3:
            if self.overcaller_has_jumped:
                bid_level = 4
            else:
                bid_level = 3
            bid = self.suit_bid(bid_level, self.overcaller_bid_one.denomination, '0628', True)
        elif self._good_support_for_overcaller():
            bid = self.suit_bid(4, suit_to_bid, '0630', True)
        elif self.hcp >= 13 and bid_level <= 4:
            bid = self.suit_bid(4, suit_to_bid, '0631', True)
        elif hand_value_points >= 11 and bid_level <= 4:
            bid = self.suit_bid(bid_level, suit_to_bid, '0632', True)
        elif self._is_weak_with_some_support_for_overcaller():
            bid = self.suit_bid(bid_level, suit_to_bid, '0633', True)
        else:
            bid = Pass('0634', True)
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _no_support_stoppers(self):
        """Return bid in NT relevant to points."""
        if self.overcaller_bid_one.level == 1:
            bid = self._no_support_stoppers_level_one()
        elif self.overcaller_bid_one.level == 2:
            bid = self._no_support_stoppers_level_two()
        else:
            bid = Pass('0635')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _no_support_stoppers_level_one(self):
        """Return bid in NT relevant to points at level 1."""
        level = self.nt_level
        if self.hcp in range(8, 12) and level <= 1:
            bid = self.nt_bid(1, '0636')
        elif self.hcp in range(12, 16) and level <= 2:
            bid = self.nt_bid(2, '0637')
        elif self.hcp >= 16 and level <= 3:
            bid = self.nt_bid(3, '0638')
        else:
            bid = Pass('0639')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _no_support_stoppers_level_two(self):
        """Return bid in NT relevant to points at level 2."""
        level = self.nt_level
        if self.hcp in range(9, 14) and level <= 2:
            bid = self.nt_bid(2, '0640')
        elif self.hcp >= 14 and level <= 3:
            bid = self.nt_bid(3, '0641')
        else:
            bid = Pass('0642')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _long_suit_bid(self):
        """Return bid based on own long suit."""
        if self.overcaller_bid_one.is_double:
            bid = self._bid_after_double()
        elif self.suit_length(self.longest_suit) >= 6 and self.hcp >= 11:
            bid = self._long_suit_after_suit()
        elif self._has_eleven_points_and_can_bid_nt():
            nt_level = self.nt_level
            if self._can_bid_five_card_major_below_nt_level():
                bid = self._long_suit_after_suit()
            else:
                if self.hcp >= 17 and self.nt_level == 1:
                    nt_level += 2
                if self.hcp >= 15 and self.nt_level == 2:
                    nt_level += 2
                elif self.hcp >= 13 and self.nt_level == 1:
                    nt_level += 1
                nt_level = min(3, nt_level)
                bid = self.nt_bid(nt_level, '0643')
        elif self._has_five_card_suit_and_seven_points():
            bid = self._long_suit_after_suit()
        elif self._has_seven_card_suit_and_shortage_in_overcallers_suit():
            bid = self.next_level_bid(self.longest_suit, '0644')
        elif self.hcp >= 6 and self.suit_length(self.overcaller_bid_one.denomination) >= 3:
            bid = self.next_level_bid(self.overcaller_bid_one.denomination, '0645')
        else:
            bid = Pass('0646')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _bid_after_double(self):
        """Show long suit after overcaller has doubled."""
        suit = self._select_suit_after_double()
        next_level = self.next_level(suit)
        level, comment = self._bid_after_double_get_level(suit, next_level)
        if self.partner_doubled_game:
            bid = Pass('0647')
        elif self._strong_in_openers_suit():
            bid = self._hold_openers_suit()
        elif self._responder_has_passed_after_one_nt_opening():
            bid = Pass('0035')
        elif self._suit_is_minor_and_can_bid_three_nt(suit, level):
            bid = self.next_nt_bid('0648')
        elif self._suit_is_minor_and_cannot_bid_three_nt(level):
            bid = Double('0649')
        elif self._has_opening_hand_and_can_bid_to_game(suit):
            bid = self.bid_to_game(suit, '0650')
        elif self._has_opening_hand_and_can_bid_to_game(self.longest_suit):
            bid = self.bid_to_game(self.longest_suit, '0650')
        elif self._overcaller_has_doubled_after_weak_two():
            if ((self.hcp >= 10 or
                    self.shape[0] >= 6) and
                    self.next_level(suit) <= 3):
                raise_level = 1
            else:
                raise_level = 0
            bid = self.next_level_bid(suit, '0651', raise_level=raise_level)
        elif self._suit_bid_allowed(level, suit):
            bid = self.suit_bid(level, suit, comment)
        elif self._distributional_strong_hand(suit):
            bid = self.next_level_bid(suit, '0652')
        elif self.last_bid.is_pass and suit not in self.opponents_suits:
            bid = self.next_level_bid(suit, '0653')
        elif self._overcaller_has_doubled_one_nt():
            bid = self.next_level_bid(self.longest_suit, '0907')
        else:
            bid = Pass('0654')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _hold_openers_suit(self):
        """Return bid when holding opener's suit."""
        suit = self._select_suit_after_double()
        if self._is_balanced_and_holds_openers_suit():
            bid = self.next_nt_bid('0655')
        elif self._has_unbid_five_four():
            if self.opener_bid_one.level == 2:
                raise_level = 1
            else:
                raise_level = 0
            bid = self.next_level_bid(suit, '0656', raise_level)
        else:
            bid = Pass('0657')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _long_suit_after_suit(self):
        """Show long suit after overcaller has bid suit."""
        if self._cannot_bid_at_this_level():
            bid = Pass('0665')
        elif self.longest_suit.is_minor and self.is_balanced and self.nt_level <= 2:
            bid = self.nt_bid(2, '0666')
        elif self._is_strong_with_good_six_card_major():
            bid = self.bid_to_game(self.longest_suit, '0667')
        elif self._is_strong_with_good_seven_card_minor():
            bid = self.bid_to_game(self.longest_suit, '0668')
        elif self._has_support_for_overcaller_and_better_points():
            bid = self.next_level_bid(self.overcaller_bid_one.denomination, '0747')
        elif self._can_bid_own_suit_after_suit():
            if self.hcp >= 15:
                bid = self.next_level_bid(self.longest_suit, '0112', raise_level=1)
            else:
                bid = self.next_level_bid(self.longest_suit, '0664')
        elif self._is_balanced_after_overcallers_minor():
            bid = self.next_nt_bid('0471')
        elif self.hcp >= 11 and self.suit_length(self.overcaller_bid_one.denomination) >= 3:
            bid = self.next_level_bid(self.overcaller_bid_one.denomination, '0413')
        elif (self.overcaller_bid_one.level >= 2 and
              self.hcp >= 7 and
              self.shape[0] >= 7 and
              self.longest_suit not in self.opponents_suits):
            bid = self.next_level_bid(self.longest_suit, '0472')
        else:
            bid = Pass('0669')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _respond_to_nt(self):
        """Respond to a NT overcall."""
        if self.is_semi_balanced:
            bid = self._respond_to_nt_semi_balanced()
        elif self._has_ten_points_and_can_bid_six_card_major():
            bid = self.bid_to_game(self.longest_suit, '0731')
        elif self._has_six_points_and_can_bid_five_card_major():
            bid = self.next_level_bid(self.five_card_major_suit, '0670')
        else:
            bid = self._respond_to_nt_distributional()
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _respond_to_nt_semi_balanced(self):
        """Respond to a NT overcall is semi_balanced."""
        if self.overcaller_bid_one.name == '1NT':
            bid = self._respond_to_one_nt_semi_balanced()
        elif self.overcaller_bid_one.name == '2NT':
            bid = self._respond_to_two_nt_semi_balanced()
        else:
            bid = self._respond_to_two_nt_semi_balanced_weak()
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _respond_to_one_nt_semi_balanced(self):
        """Respond to 1NT overcall is semi_balanced."""
        if self._can_bid_stayman_after_overcallers_one_nt():
            bid = self.club_bid(2, '0671')
        elif self._can_bid_stayman_after_overcallers_two_nt():
            bid = self.club_bid(3, '0672')
        elif 8 <= self.hcp <= 9 and self.nt_level <= 2:
            bid = self.nt_bid(2, '0673')
        elif self._has_six_card_major_and_can_bid_game():
            bid = self.suit_bid(4, self.longest_suit, '0067')
        elif self._has_nine_points_and_four_card_major():
            bid = self.next_level_bid(self.longest_suit, '0125', raise_level=1)
        elif self.hcp >= 10 and self.nt_level <= 3:
            bid = self.nt_bid(3, '0674')
        else:
            bid = Pass('0675')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _respond_to_two_nt_semi_balanced(self):
        """Respond to 2NT overcall is semi_balanced."""
        if self._has_eight_points_and_five_card_major():
            bid = self.next_level_bid(self.five_card_major_suit, '0676')
        elif self._overcaller_bid_nt_and_four_card_major():
            bid = self.suit_bid(3, self.club_suit, '0928')
        elif self.hcp >= 8 and self.nt_level <= 3:
            bid = self.nt_bid(3, '0677')
        else:
            bid = self._respond_to_two_nt_semi_balanced_weak()
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _respond_to_two_nt_semi_balanced_weak(self):
        """Respond to 2NT overcall is semi_balanced with weak hand."""
        if self.hcp >= 4 and self.nt_level <= 3 and self.opener_bid_one.level == 1:
            bid = self.nt_bid(3, '0678')
        else:
            bid = Pass('0679')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _respond_to_nt_distributional(self):
        """Respond to a NT overcall if distributional."""
        if (self.overcaller_bid_one.name == '2NT' and
                self.opener_bid_one.level == 1):
            bid = self._respond_to_nt_distributional_overcaller_jumped()
        elif self.hcp >= 4:
            bid = self._respond_to_nt_after_weak_2()
        else:
            bid = Pass('0680')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _respond_to_nt_after_weak_2(self):
        """Return bid after opener bid weak 2"""
        suit = self._select_suit()
        bid = self.next_level_bid(suit)
        if bid.name == '2C':
            bid = self._respond_to_nt_distributional_with_clubs()
        elif (self.suit_length(suit) >= 5 and
                suit not in self.opponents_suits and
                self.next_level(suit) < self.bid_to_game(suit).level and
                suit != self.club_suit):
            bid = self.next_level_bid(suit, '0681')
        elif self._is_five_four_or_five_five():
            suit = self.longest_suit
            if suit in self.opponents_suits:
                suit = self.second_suit
            if self.next_level(suit) < self.bid_to_game(suit).level:
                bid = self.next_level_bid(suit, '0682')
            else:
                bid = Pass('0000')
        elif self.opener_bid_one.level == 2 and self.overcaller_bid_one.name == '2NT':
            bid = self._nt_after_weak_opening()
        else:
            bid = Pass('0683')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _nt_after_weak_opening(self):
        """Return bid after overcaller bids NT after weak 2 opening."""
        if self.hcp <= 6:
            bid = Pass('0684')
        elif self.four_card_major_suit and self.next_level(self.club_suit) <= 3:
            bid = self.next_level_bid(self.club_suit, '0685')
        elif self.nt_level <= 3:
            bid = self.nt_bid(3, '0686')
        else:
            bid = Pass('0687')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _respond_to_nt_distributional_with_clubs(self):
        """Respond to a NT overcall if best suit is clubs."""
        if self.hcp >= 8:
            bid = self.nt_bid(2, '0688')
        else:
            bid = Pass('0689')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _respond_to_nt_distributional_overcaller_jumped(self):
        """Respond to a jump NT overcall is distributional."""
        if self._can_bid_five_card_major_at_level_three():
            bid = self.suit_bid(3, self.longest_suit, '0690')
        else:
            bid = Pass('0691')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    # Various utility functions

    def _fourth_suit_bid(self, suit):
        """Return True if suit is fourth suit bid."""
        value = False
        suits = [0, 0, 0, 0]
        suits[suit.rank] = 1
        for bid in self.bid_history:
            if Bid(bid).is_suit_call:
                bid_suit = Bid(bid).denomination.rank
                suits[bid_suit] = 1
        if sum(suits) == 4:
            value = True
        return value

    def _select_suit(self, force_major=False):
        """Return best suit to bid."""
        suit_one, suit_two = self._top_two_unbid_suits()
        suit_one_holding = self.suit_length(suit_one)
        suit_two_holding = self.suit_length(suit_two)
        if (suit_one_holding == suit_two_holding or
                (suit_one_holding == 5 and suit_two_holding == 4 and
                 suit_one.is_minor and suit_two.is_major)):
            if suit_two.is_major:
                suit = self.cheaper_suit(suit_one, suit_two)
            elif suit_one.is_major:
                suit = suit_one
            elif (suit_one.is_major and
                  suit_one_holding == suit_two_holding):
                suit = suit_one
                if not force_major and suit_one_holding == suit_two_holding:
                    suit = self.cheaper_suit(suit_one, suit_two)
            else:
                suit = self.cheaper_suit(suit_one, suit_two)
        else:
            suit = suit_one
        if suit == self.opener_bid_one.denomination or suit == self.responder_bid_one.denomination:
            if suit_two_holding >= 0:
                suit = suit_two
            else:
                suit = self.no_trumps
        return suit

    def _top_two_unbid_suits(self):
        """Return two longest unbid suits."""
        suit_index = 0
        suit_offset = 1
        found = False
        # Loop through suits to find two longest unbid suits.
        suit_one, suit_two = None, None
        while not found:
            suit_one = self.ordered_holding[suit_index][1]
            suit_two = self.ordered_holding[suit_index+suit_offset][1]
            if (suit_one == self.opener_bid_one.denomination or
                    suit_one == self.responder_bid_one.denomination):
                suit_index += 1
            elif (suit_two == self.opener_bid_one.denomination or
                  suit_two == self.responder_bid_one.denomination):
                suit_offset += 1
            else:
                found = True
        return suit_one, suit_two

    def _can_bid_to_game(self, suit):
        """Return True if conditions are met for raise to game."""
        value = False
        sufficient_points = (self.hcp >= 8 or
                             (self.hcp >= 7 and self.shape[3] <= 1))
        if (self.suit_length(suit) >= 2 and
                sufficient_points and
                not self.is_insufficient_bid(self.bid_to_game(suit)) and
                (self.opener_bid_one.level == 1 or
                 suit.is_major)):
            value = True
        return value

    def _find_level_for_major_raise(self, major_suit):
        """Return the appropriate raise level for major suit  support."""
        if self.next_level(major_suit) >= 4:
            raise_level = 0
        elif self.hcp >= 13:
            raise_level = 2
        elif self.hcp >= 10:
            raise_level = 1
        else:
            raise_level = 0
        return raise_level

    def _find_four_card_major(self):
        """Return an unbid four card major."""
        if self.spades >= 4 and self.spade_suit not in self.opponents_suits:
            suit = self.spade_suit
        elif (self.hearts >= 4 and
              self.heart_suit not in self.opponents_suits):
            suit = self.heart_suit
        else:
            suit = None
        return suit

    def _leave_double(self):
        value = False
        suit = self._select_suit()
        openers_suit = Bid(self.bid_history[-3]).denomination
        if (suit.is_minor and
                self.suit_length(openers_suit) >= 4 and
                self.hcp >= 10 and
                Bid(self.bid_history[-1]).is_pass):
            value = True
        return value

    def _get_hand_value_points(self, suit):
        """Return hand value points."""
        suit_cards = self.suit_length(suit)
        hand_value_points = (self.hcp +
                             self.support_shape_points(suit) +
                             suit_cards - 3)
        if self.shape[3] == 0:
            hand_value_points += 1
        return hand_value_points

    def _select_suit_after_double(self):
        five_four = (self.five_four and
                     (self.longest_suit in self.opponents_suits or
                      self.second_suit in self.opponents_suits))
        if self.five_five:
            if (self.longest_suit.rank < self.second_suit.rank and
                    self.second_suit not in self.opponents_suits):
                suit = self.second_suit
            elif self.longest_suit not in self.opponents_suits:
                suit = self.longest_suit
            else:
                suit = self.second_suit
        elif five_four:
            if self.longest_suit not in self.opponents_suits:
                suit = self.longest_suit
            else:
                suit = self.second_suit
        else:
            suit = self._select_suit(force_major=True)
        return suit

    def _suit_bid_allowed(self, level, suit):
        """Return True if a suit bid is allowed."""
        double_forcing = Bid(self.bid_history[-1]).is_pass
        sufficient_points = (self.hcp >= 9 or level <= 2)
        level_low_enough = (self.next_level(suit) <= 4 and level >= self.next_level(suit))

        if not double_forcing and self.suit_length(suit) < 4:
            return False
        elif double_forcing and suit not in self.opponents_suits:
            return True
        elif (sufficient_points and
                level_low_enough and
                suit not in self.opponents_suits):
            return True
        return False

    def _bid_after_double_get_level(self, suit, level):
        """Return level and comment with a long suit after a double."""
        comment = '0658'
        if self.opener_bid_one.level == 1:
            if self.responder_bid_one.is_value_call:
                if self.hcp >= 12:
                    level += 1
                comment = '0659'
            else:
                comment = '0660'
                if (self.hcp >= 13 and suit.is_major and
                        self.suit_length(suit) >= 5):
                    level = 4
                    comment = '0661'
                elif self.hcp >= 12:
                    level += 2
                elif self.hcp >= 9 and level == 1:
                    level += 1
        elif self.opener_bid_one.level == 2:
            comment = '0662'
            level = self.next_level(suit)
            if self.hcp >= 8:
                level = max(3, level)
            else:
                level = max(2, level)
        elif self.opener_bid_one.level == 3:
            comment = '0663'
            level = self.next_level(suit)
            if self.hcp >= 8:
                level = max(4, level)
            else:
                level = max(3, level)
        return level, comment

    # Various boolean functions

    def _overcall_bid_at_three_level(self):
        """Return True if overcaller has bid at level 3."""
        result = (self.overcaller_bid_one.level >= 3 and
                  self.opener_bid_one.level != 3)
        return result

    def _has_biddable_eight_card_suit(self):
        """Return True if with biddable 8 card suit."""
        result = (self.shape[0] == 8 and
                  self.next_level(self.longest_suit) <= self.longest_suit.game_level and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _has_three_card_support_for_overcallers_major(self):
        """Return True if 3 card support for overcaller's major."""
        result = (self.overcaller_bid_one.is_major and
                  self.suit_length(self.overcaller_bid_one.denomination) >= 3)
        return result

    def _is_weak_no_support_for_overcaller(self):
        """Return True if weak and no support for overcaller."""
        result = (self.bid_history[-1] == 'P' and
                  8 <= self.hcp <= 9 and
                  self.suit_length(self.overcaller_bid_one.denomination) <= 2 and
                  self.shape[0] <= 5 and
                  self.nt_level == 1 and
                  self.stoppers_in_bid_suits)
        return result

    def _has_biddable_suit(self):
        """Return True if hand has a biddable suit."""
        biddable_six_card_suit = (self.shape[0] >= 6 and
                                  self.suit_length(self.overcaller_bid_one.denomination) <= 2)
        can_compete_after_nt = (self.opener_bid_one.name == '1NT' and
                                self.overcaller_bid_one.is_suit_call and
                                self.overcaller_bid_one.level == 2 and
                                self.hcp >= 10)
        if (self.suit_length(self.longest_suit) == self.suit_length(self.second_suit) and
                self.second_suit == self.overcaller_bid_one.denomination):
            my_suit = self.second_suit
        else:
            my_suit = self.longest_suit
        has_own_five_card_suit = (self.suit_length(self.overcaller_bid_one.denomination) <= 1 and self.shape[0] >= 5)
        has_own_five_card_major = (self.hcp >= 8 and self.shape[0] >= 5 and my_suit.is_major)
        can_bid_own_suit = (self.hcp >= 8 and
                            self.shape[0] >= 5 and
                            self.responder_bid_one.is_value_call and
                            self.overcaller_bid_one.is_minor and
                            my_suit.is_major)
        result = (biddable_six_card_suit or
                  can_bid_own_suit or
                  can_compete_after_nt or
                  has_own_five_card_major or
                  has_own_five_card_suit)
        return result

    def _can_bid_nt_opposition_has_no_fit(self):
        """Return True if opposition weak or no fit can bid nt."""
        result = (self.stoppers_in_bid_suits and
                  (not self.responder_bid_one.is_pass or
                   self.hcp >= 16) and
                  (self.opener_bid_one.denomination != self.responder_bid_one.denomination or
                   self.responder_bid_one.level <= 2))
        return result

    def _can_support_overcaller(self):
        """Return True if can support overcaller."""
        if self.overcaller_has_jumped:
            support_for_overcaller = 2
        else:
            support_for_overcaller = 3
        result = self.suit_length(self.overcaller_bid_one.denomination) >= support_for_overcaller
        return result

    def _has_opening_values_can_bid_nt(self):
        """Return True if opening values and can bid nt."""
        result = (self.is_balanced and
                  self.hcp >= 11 and
                  not self.responder_bid_one.is_value_call and
                  self.stoppers_in_bid_suits)
        return result

    def _can_bid_six_card_suit_at_three_level(self):
        """Return True if can bid 6 card suit at level 3."""
        result = (self.shape[0] >= 6 and
                  self.hcp >= 10 and
                  self.next_level(self.longest_suit) <= 3 and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _has_ten_points_and_stoppers(self):
        """Return True if 10 points and can bid 3NT."""
        result = (self.hcp >= 10 and
                  self.overcaller_bid_one.denomination.is_minor and
                  self.stoppers_in_bid_suits and
                  self.nt_level == 3)
        return result

    def _has_eight_points_and_stoppers(self):
        """Return True if eight points and stoppers."""
        result = (self.hcp >= 8 and
                  self.stoppers_in_unbid_suits() and
                  self.nt_level == 3)
        return result

    def _has_eleven_points_balanced_and_responder_has_bid_game(self):
        """Return True if 11 points and responder at game."""
        result = (self.hcp >= 11 and
                  self.shape[0] == 4 and
                  self.responder_bid_one.is_game)
        return result

    def _is_weak_and_intervening_bid(self):
        """Return True if weak after overcaller has doubled."""
        double_index = self.bid_history.index('D')
        next_bid = Bid(self.bid_history[double_index+1])
        result = (next_bid.is_suit_call and
                  self.hcp <= 5 and
                  self.shape[0] <= 5)
        return result

    def _weak_and_responder_has_bid(self):
        """Return True if weak and responder has bid."""
        result = (self.hcp <= 5 and
                  not self.responder_bid_one.is_pass and
                  self.responder_bid_one.level <= 2)
        return result

    def _has_ten_points_and_opening_bid_is_weak_three(self):
        """Return True if 10+ points and opener has bid at 3 level."""
        result = (self.opener_bid_one.level == 3 and
                  self.nt_level <= 3 and
                  self.hcp >= 10)
        return result

    def _has_thirteen_points_and_five_card_major(self):
        """Return True if 13 points and five card major."""
        result = (self.overcaller_bid_one.denomination.is_minor and
                  self.five_card_major_or_better and
                  self.hcp >= 13)
        return result

    def _has_ten_points_overcaller_bid_minor(self):
        """Return True if 10 points and overcaller bid minor."""
        result = (self.overcaller_bid_one.is_minor and
                  self.is_semi_balanced and
                  self.stoppers_in_bid_suits and
                  self.hcp >= 10 and
                  not Bid(self.bid_history[-1]).is_value_call)
        return result

    def _can_support_overcaller_at_given_level(self, level):
        """Return True if can support overcaller at level 2."""
        hand_value_points = self._get_hand_value_points(self.overcaller_bid_one.denomination)
        if level == 2:
            points_range = range(8, 13)
        elif level == 3:
            points_range = range(12, 16)
        elif level == 4:
            points_range = range(16, 40)
        else:
            points_range = range(0, 0)
        result = (hand_value_points in points_range and
                  self.next_level(self.overcaller_bid_one.denomination) <= level)
        return result

    def _opening_hand_and_overcaller_bid_minor(self):
        """Return True if opening hand and overcaller bids minor."""
        result = (self.hcp >= 13 and
                  self.overcaller_bid_one.denomination.is_minor and
                  self.stoppers_in_bid_suits and
                  self.nt_level <= 3)
        return result

    def _ten_points_and_overcaller_bid_minor(self):
        """Return True if 10+ points and overcaller bids minor."""
        result = (self.hcp >= 10 and
                  self.overcaller_bid_one.denomination.is_minor and
                  self.stoppers_in_bid_suits and
                  self.is_semi_balanced and
                  self.nt_level <= 2)
        return result

    def _good_support_for_overcaller(self):
        """Return True if good support for overcaller."""
        hand_value_points = self._get_hand_value_points(self.overcaller_bid_one.denomination)
        result = (self.overcaller_bid_one.level <= 4 and
                  self.next_level(self.overcaller_bid_one.denomination) <= 4 and
                  (self.hcp >= 16 or
                   (hand_value_points >= 14 and
                    self.suit_length(self.overcaller_bid_one.denomination) >= 5)))
        return result

    def _is_weak_with_some_support_for_overcaller(self):
        """Return True if weak with some support for overcaller."""
        result = (self.suit_length(self.overcaller_bid_one.denomination) >= 4 and
                  self.suit_points(self.overcaller_bid_one.denomination) >= 1 and
                  self.hcp >= 5 and
                  self.opener_bid_one.level == 2)
        return result

    def _has_eleven_points_and_can_bid_nt(self):
        """Return True if 11 points and can bid nt."""
        result = (self.stoppers_in_bid_suits and
                  self.hcp >= 11 and
                  self.nt_level <= 3)
        return result

    def _can_bid_five_card_major_below_nt_level(self):
        """Return True if can bid 5 card major."""
        result = (self.next_level(self.longest_suit) <= self.nt_level and
                  self.shape[0] >= 5 and
                  self.longest_suit.is_major)
        return result

    def _has_five_card_suit_and_seven_points(self):
        """Return True if 7 points and 5 card suit."""
        suit = self._select_suit()
        result = (suit.is_suit and
                  self.suit_length(suit) >= 5 and
                  self.hcp >= 7 and
                  not self.opener_bid_two.is_nt)
        return result

    def _has_seven_card_suit_and_shortage_in_overcallers_suit(self):
        """Return True if 7 card suit and shortage in overcallers suit."""
        result = (self.suit_length(self.overcaller_bid_one.denomination) <= 1 and
                  self.shape[0] >= 7 and
                  self.hcp >= 3 and
                  self.next_level(self.longest_suit) <= 2 and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _strong_in_openers_suit(self):
        """Return True if strong in openers suit."""
        result = (self.opener_bid_one.is_suit_call and
                  ((self.hcp >= 8 and
                    self.suit_length(self.opener_bid_one.denomination) >= 4) or
                   (self.hcp >= 6 and
                    self.suit_length(self.opener_bid_one.denomination) >= 5)))
        return result

    def _responder_has_passed_after_one_nt_opening(self):
        """Return True if 7 points and responder passes after 1NT."""
        result = (self.opener_bid_one.is_nt and
                  self.hcp >= 7 and
                  self.responder_bid_one.is_pass)
        return result

    def _suit_is_minor_and_can_bid_three_nt(self, suit, level):
        """Return True if suit is minor and level over 3 NT."""
        result = (10 <= self.hcp <= 12 and
                  level >= 4 and
                  suit.is_minor and
                  self.stoppers_in_bid_suits)
        return result

    def _suit_is_minor_and_cannot_bid_three_nt(self, level):
        """Return True if suit is minor and level over 3 NT."""
        result = (self.hcp >= 8 and
                  level >= 4 and
                  self.responder_bid_one.denomination.is_minor and
                  not self.overcaller_bid_one.is_double)
        return result

    def _has_opening_hand_and_can_bid_to_game(self, suit):
        """Return True if opening hand and can bid to game in suit."""
        double_level = self.double_level()
        game_level = self.game_level(suit)
        next_level = self.next_level(suit)
        result = (self.hcp >= 13 and
                  double_level == 3 and
                  next_level <= game_level)
        return result

    def _overcaller_has_doubled_after_weak_two(self):
        """Return True if overcaller has doubled after weak two opening."""
        result = (self.hcp >= 6 and
                  self.opener_bid_one.level == 2 and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _distributional_strong_hand(self, suit):
        """Return True if distributional hand."""
        result = (self.hcp + self.distribution_points >= 12 and
                  self.next_level(suit) <= 4 and
                  suit not in self.opponents_suits)
        return result

    def _overcaller_has_doubled_one_nt(self):
        """Return True if overcaller has doubled 1NT."""
        result = (self.opener_bid_one.name == '1NT' and
                  self.overcaller_bid_one.is_double and
                  self.hcp >= 6 and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _is_balanced_and_holds_openers_suit(self):
        """Return True if balanced and holds openers suit."""
        result = (self.hcp >= 8 and
                  self.is_balanced and
                  self.stoppers_in_bid_suits)
        return result

    def _has_unbid_five_four(self):
        """Return True if unbid 5/4 suits."""
        result = (self.hcp >= 8 and
                  self.five_four and
                  (self.longest_suit not in self.opponents_suits or
                   self.second_suit not in self.opponents_suits))
        return result

    def _cannot_bid_at_this_level(self):
        """Return True if cannot make a sensible bid at this level."""
        level = self.next_level(self.longest_suit)
        jump = self.is_jump(self.opener_bid_one, self.overcaller_bid_one)
        cannot_bid_at_level_three = (level >= 3 and self.hcp <= 11 and self.shape[0] <= 4 and not jump)
        cannot_bid_at_level_two = (level >= 2 and self.hcp <= 9 and self.shape[0] <= 5 and not jump)
        result = (level >= 7 or
                  cannot_bid_at_level_three or
                  cannot_bid_at_level_two or
                  self.hcp < 6)
        return result

    def _is_strong_with_good_six_card_major(self):
        """Return True if strong with good six card major."""
        result = (self.shape[0] >= 6 and
                  self.hcp >= 15 and
                  self.suit_points(self.longest_suit) >= 8 and
                  self.longest_suit.is_major and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _is_strong_with_good_seven_card_minor(self):
        """Return True if strong with good 7 card minor."""
        result = (self.shape[0] >= 7 and
                  self.hcp >= 15 and
                  self.suit_points(self.longest_suit) >= 8 and
                  self.longest_suit.is_minor and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _can_bid_own_suit_after_suit(self):
        """Return True if can bid own suit."""
        result = ((self.next_level(self.longest_suit) <= 2 or
                   self.hcp >= 10 or
                   self.longest_suit.is_major) and
                  (self.hcp >= 10 or not self._fourth_suit_bid(self.longest_suit)) and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _has_six_points_and_can_bid_five_card_major(self):
        """Return True if 6+ points and can bid 5 card major."""
        result = (self.five_card_major_suit and
                  self.five_card_major_suit not in self.opponents_suits and
                  self.hcp >= 6 and
                  self.next_level(self.longest_suit) <= 4)
        return result

    def _has_ten_points_and_can_bid_six_card_major(self):
        """Return True if 10+ points and can bid 6 card major."""
        result = (self.shape[0] >= 6 and
                  self.longest_suit.is_major and
                  self.longest_suit not in self.opponents_suits and
                  self.hcp >= 10 and
                  self.next_level(self.longest_suit) <= 4)
        return result

    def _can_bid_stayman_after_overcallers_one_nt(self):
        """Return True if 4 card major over overcallers 1NT."""
        result = (self.overcaller_bid_one.name == '1NT' and
                  self.four_card_major_suit and
                  self.suit_length(self.four_card_major_suit) == 4 and
                  self.hcp >= 8 and
                  self.next_level(self.club_suit) <= 2)
        return result

    def _can_bid_stayman_after_overcallers_two_nt(self):
        """Return True if 4 card major over overcallers 2NT."""
        result = (self.overcaller_bid_one.name == '2NT' and
                  self.four_card_major_suit and
                  self.hcp >= 6)
        return result

    def _has_six_card_major_and_can_bid_game(self):
        """Return True if six_card_major."""
        result = (self.shape[0] >= 6 and
                  self.longest_suit.is_major and
                  self.next_level(self.longest_suit) <= 4 and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _has_nine_points_and_four_card_major(self):
        """Return True if has 9 points and 4 card major."""
        result = (self.four_card_major_or_better and
                  self.hcp >= 9 and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _has_eight_points_and_five_card_major(self):
        """Return True if 6 points and a five card major."""
        result = (self.five_card_major_suit and
                  self.five_card_major_suit not in self.opponents_suits and
                  self.hcp >= 8)
        return result

    def _is_five_four_or_five_five(self):
        """Return True if 5/4 or 5/5."""
        result = ((self.five_four or
                   self.five_five) and
                  (self.longest_suit not in self.opponents_suits or
                   self.second_suit not in self.opponents_suits))
        return result

    def _can_bid_five_card_major_at_level_three(self):
        """Return True if can bid 5 card major at level 3."""
        result = (self.longest_suit.is_major and
                  self.longest_suit not in self.opponents_suits and
                  self.suit_length(self.longest_suit) >= 5 and
                  self.next_level(self.longest_suit) == 3)
        return result

    def _is_balanced_after_overcallers_minor(self):
        """Return True if balanced and stoppers in bid suit."""
        result = (self.hcp >= 11 and
                  self.is_balanced and
                  self.overcaller_bid_one.denomination.is_minor and
                  self.stoppers_in_bid_suits)
        return result

    def _has_strength_and_support_for_overcallers_three_level_bid(self):
        """Return True if 10 points and supporter for overcaller."""
        result = (self.overcaller_bid_one.level == 3 and
                  self.overcaller_bid_one.denomination.is_major and
                  self.hcp >= 10 and
                  self.suit_length(self.overcaller_bid_one.denomination) >= 3 and
                  self.next_level(self.overcaller_bid_one.denomination) <= 4)
        return result

    def _has_support_for_overcaller_and_better_points(self):
        """Return True if support and better points in overcaller's suit."""
        result = (self.suit_length(self.overcaller_bid_one.denomination) >= 4 and
                  self.suit_points(self.overcaller_bid_one.denomination) >= 5 and
                  self.suit_points(self.longest_suit) <= 3)
        return result

    def _overcaller_bid_nt_and_four_card_major(self):
        """Return True if overcall has bid no trumps and a 4 card major."""
        result = (self.hcp >= 8 and 
                  self.longest_suit.is_major and
                  self.next_level(self.club_suit) <= 3)
        return result

    # def xxx(self):
    #     """Return True if xxx."""
    #     result = False
    #     return result

    # def xxx(self):
    #     """Return True if xxx."""
    #     result = False
    #     return result
