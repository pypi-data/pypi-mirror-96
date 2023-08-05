""" Bid for Game
    Acol OverCallersBid module
"""

import inspect
from .bridge_tools import Bid, Pass, Double
from .bidding_hand import BiddingHand


class OverCallersRebid(BiddingHand):
    """BfG OverCallersRebid class."""
    def __init__(self, hand_cards, board):
        super(OverCallersRebid, self).__init__(hand_cards, board)
        self.trace = 0

    def suggested_bid(self):
        """Direct control to relevant method and return a Bid object."""
        if self._can_double():
            bid = Double('0692')
        elif self._very_strong_six_card_suit_advancer_bids_game():
            bid = self.suit_bid(6, self.longest_suit, '0693')
        elif self.bid_one.is_pass:
            bid = Pass('0694')
        elif self._advancer_bids_three_nt_and_long_suit():
            bid = self.bid_to_game(self.longest_suit, '0311')
        elif self.advancer_bid_one.is_game:
            bid = Pass('0695')
        elif self._advancer_supports_overcaller_suit():
            bid = self._partner_shows_support()
        elif self.advancer_bid_one.is_nt and self.is_semi_balanced:
            bid = self._bid_after_nt_agreed()
        elif self.advancer_bid_one.is_suit_call:
            bid = self._partner_bid_suit()
        elif self.bid_one.is_double:
            bid = self._rebid_after_double_pass()
        elif self.hcp >= 15 and self.shape[0] >= 6:
            bid = self._rebid_long_suit()
        elif self.advancer_bid_one.is_value_call and self.shape[0] >= 7:
            bid = self._rebid_long_suit()
        elif self._advancer_bids_two_nt_and_six_card_suit_and_weak():
            bid = self.next_level_bid(self.longest_suit, '0462')
        elif self._strong_over_weak_three():
            bid = Double('0691')
        elif (self.opener_bid_one.is_suit_call and
              self.opener_bid_one.denomination == self.responder_bid_one.denomination):
            bid = Pass('0696')
        elif self.hcp >= 13 and self.five_five:
            bid = self._strong_five_five_hand()
        elif self._has_long_suit():
            bid = self._rebid_long_suit()
        elif self.shape[0] >= 6:
            bid = self._six_card_suit_bid()
        elif self._can_bid_second_suit_at_level_two():
            bid = self.suit_bid(2, self.second_suit, '0652')
        elif self._can_rebid_longest_suit_at_level_two():
            bid = self.next_level_bid(self.longest_suit, '0697')
        elif self._can_rebid_second_suit_at_level_two():
            bid = self.next_level_bid(self.second_suit, '0698')
        elif self._can_bid_second_suit():
            bid = self.next_level_bid(self.second_suit, '0569')
        else:
            bid = Pass('0699')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _bid_after_nt_agreed(self):
        """Bid after NT agreed."""
        if self._strong_with_biddable_five_card_major():
            bid = self._bid_five_card_major()
        elif self.nt_level <= 3 and self.hcp >= 17:
            bid = self.nt_bid(3, '0700')
        elif self.hcp <= 14 and self.shape[0] >= 6:
            bid = self.next_level_bid(self.longest_suit, '0701')
        elif self._can_rebid_nt_at_three_level():
            bid = self.nt_bid(3, '0702')
        elif self._can_rebid_second_suit_at_level_two():
            raise_level = 0
            suit = self.second_suit
            if self.second_suit in self.opponents_suits:
                suit = self.longest_suit
                if self.hcp >= 14:
                    raise_level = 1
            bid = self.next_level_bid(suit, '0703', raise_level)
        else:
            bid = Pass('0704')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _bid_five_card_major(self):
        """Return bid after NT agreed with 5 card major."""
        suit = self._biddable_five_card_major()
        if self._is_competitive_auction():
            if self.hcp >= 19 and self.next_level(suit) <= 4:
                bid = self.suit_bid(4, suit, '0705')
            elif self.next_level(suit) <= 3:
                bid = self.suit_bid(3, suit, '0036')
            else:
                bid = Pass('0000')
        elif self._strong_and_advancer_bids_two_nt():
            bid = self.nt_bid(3, '0047')
        elif self.next_level(suit) <= 2:
            bid = self.suit_bid(2, suit, '0037')
        else:
            bid = Pass('0000')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _strong_five_five_hand(self):
        """Bid with strong  5/5 hand."""
        suit = self._five_five_second_suit()
        bid = self.next_level_bid(suit, '0708')
        if bid.level >= 4:
            bid = Pass('0709')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _six_card_suit_bid(self):
        """Bid with a 6+ card suit."""
        if self._can_show_second_suit_after_advancer_has_bid():
            bid = self.next_level_bid(self.second_suit, '0710')
        elif self._can_bid_six_card_suit_in_competitive_auction():
            bid = self.next_level_bid(self.longest_suit, '0711')
        elif self.advancer_bid_one.is_nt:
            bid = self.next_level_bid(self.bid_one.denomination, '0712')
        else:
            bid = Pass('0713')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _rebid_long_suit(self):
        """Rebid own long suit."""
        if self._can_rebid_suit_after_advancer_has_bid():
            bid = self.next_level_bid(self.bid_one.denomination, '0714')
        elif self.shape[0] >= 7 and self.next_level(self.longest_suit) <= 2:
            bid = self.next_level_bid(self.longest_suit, '0937')
        else:
            bid = Pass('0715')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _rebid_after_double(self):
        """Rebid after double."""
        suit_for_rebid = self._get_best_suit_for_rebid()
        if self._weak_hand_after_opener_bids_weak_two():
            bid = Pass('0716')
        elif self._minimum_after_double_over_1nt():
            bid = Pass('0857')
        elif self.is_balanced and self.hcp >= 22 and self.nt_level <= 3:
            bid = self._exceptional_major_or_nt()
        elif self.hcp >= 18 and self.nt_level <= 2:
            bid = self._rebid_after_double_strong()
        elif self._is_strong_in_opponents_suit():
            bid = Pass('0402')
        elif self._strong_and_no_support_for_advancer(suit_for_rebid):
            bid = self.next_level_bid(suit_for_rebid, '0717')
        elif self._very_strong_and_can_bid_nt():
            bid = self.next_nt_bid('0718')
        elif self._can_support_advancer_after_double():
            bid = self._no_long_suit_support_partner()
        elif self.suit_length(self.advancer_bid_one.denomination) >= 4:
            bid = self.next_level_bid(self.advancer_bid_one.denomination, '0719')
        elif self._suit_for_rebid_is_minor_after_double(suit_for_rebid):
            bid = self.next_level_bid(self.advancer_bid_one.denomination, '0720')
        elif self._strong_and_can_bid_rebid_suit(suit_for_rebid):
            bid = self.next_level_bid(suit_for_rebid, '0721')
        else:
            bid = self._rebid_suit_for_rebid()
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _exceptional_major_or_nt(self):
        """Bid major or NT on very exceptional hand."""
        if self._can_bid_five_card_major_at_three_level():
            bid = self.suit_bid(3, self.longest_suit, '0722')
        else:
            bid = self.nt_bid(3, '0723')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _no_long_suit_support_partner(self):
        """Bid with no long suit and 3+ card support for partner."""
        if self.advancer_bid_one.level >= 4:
            if self.hcp + self.distribution_points >= 21:
                bid = self.next_level_bid(self.advancer_bid_one.denomination, '0724')
            else:
                bid = Pass('0725')
        elif self._has_opponents_suit(self.bid_history[-1]):
            bid = Pass('0726')
        elif self._strong_balanced_and_advancer_bids_minor():
            bid = self.nt_bid(3, '0246')
        elif self._above_minimum_and_advancer_bids_after_double():
            if self._can_raise_advancer_after_double():
                raise_level = 1
            else:
                raise_level = 0
            bid = self.next_level_bid(self.advancer_bid_one.denomination, '0727', raise_level)
        elif self._support_for_partners_level_three_call():
            bid = self.next_level_bid(self.partner_bid_one.denomination, '0784')
        else:
            bid = Pass('0728')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _rebid_suit_for_rebid(self):
        """Bid with weak hand and no support for/from partner."""
        if self.shape[0] >= 5:
            suit_for_rebid = self.longest_suit
        else:
            suit_for_rebid = self._cheapest_four_card_suit()
        if self._partner_weak_after_double():
            bid = Pass('0668')
        elif self._is_balanced_with_stopper(suit_for_rebid):
            bid = self.nt_bid(self.nt_level, '0729')
        elif suit_for_rebid not in self.opponents_suits:
            chosen_suit = self._select_suit_for_rebid()
            bid = self.next_level_bid(chosen_suit, '0730')
        else:
            bid = Pass('0731')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _rebid_after_double_strong(self):
        """Rebid after Double with a strong hand."""
        suit_for_rebid = self._get_best_suit_for_rebid()
        if self._four_card_support_for_advancers_major():
            bid = self._support_partners_major(self.advancer_bid_one.denomination)
        elif self._can_bid_five_card_major_at_two_level(suit_for_rebid):
            if suit_for_rebid not in self.opponents_suits:
                bid = self.suit_bid(2, suit_for_rebid, '0732')
            else:
                bid = self.next_nt_bid('0733')
        elif self._very_strong_and_some_support_for_partner():
            bid = self.bid_to_game(self.partner_last_bid.denomination, '0572')
        elif self._has_five_card_suit_and_no_support_from_advancer(suit_for_rebid):
            bid = self._five_card_suit_and_no_support_from_advancer()
        else:
            bid = self.next_nt_bid('0736')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _five_card_suit_and_no_support_from_advancer(self):
        if self.longest_suit in self.opponents_suits:
            suit_for_rebid = self.second_suit
        else:
            suit_for_rebid = self.longest_suit
        if self._is_balanced_and_long_suit_is_minor(suit_for_rebid):
            bid = self.next_nt_bid('0260')
        elif self._has_three_card_support_for_advancers_major(suit_for_rebid):
            bid = self._support_partners_major(self.advancer_bid_one.denomination)
        elif suit_for_rebid not in self.opponents_suits:
            bid = self.next_level_bid(suit_for_rebid, '0734')
        else:
            bid = Pass('0735')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _support_partners_major(self, partners_suit):
        """Bid with support for partners major."""
        level = self.next_level(partners_suit)
        if self.opener_bid_two.is_value_call:
            previous_bid = self.opener_bid_two
        elif self.responder_bid_one.is_value_call:
            previous_bid = self.responder_bid_one
        elif self.opener_bid_one.is_value_call:
            previous_bid = self.opener_bid_one
        else:
            assert False, 'previous_bid not assigned'
        if self.is_jump(previous_bid, self.advancer_bid_one):
            if level < 4:
                level = 4
            comment = '0737'
        else:
            comment = '0738'
        bid = self.suit_bid(level, partners_suit, comment)
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _rebid_after_double_pass(self):
        """Rebid after overcall Double and partner has passed."""
        suit = Bid(self.bid_history[-3]).denomination
        if self.bid_history[-1] == 'P' and self.bid_history[-2] == 'P' and self.suit_length(suit) >= 4 and self.suit_points(suit) >= 6:
            bid = Pass('0930')
        elif self._strong_and_opposition_weak():
            bid = Double('0740')
        elif self._is_strong_has_five_five():
            bid = self._strong_with_five_five()
        elif self._is_strong_with_good_five_card_suit():
            bid = self.next_level_bid(self.longest_suit, '0739')
        elif self.advancer_bid_one.is_double and not self.opponents_at_game:
            bid = self.next_level_bid(self.longest_suit, '0739')
        elif self._is_strong_and_balanced():
            bid = self.nt_bid(2, '0743')
        elif self._is_medium_and_balanced():
            bid = self.nt_bid(2, '0744')
        else:
            bid = Pass('0745')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _strong_with_five_five(self):
        if self.longest_suit in self.opponents_suits:
            suit_for_rebid = self._five_five_second_suit()
        else:
            suit_for_rebid = self.longest_suit
        if self.suit_points(suit_for_rebid) >= 5:
            bid = self.next_level_bid(suit_for_rebid, '0741')
        else:
            bid = Pass('0742')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _partner_bid_suit(self):
        """Respond after partner has bid a suit."""
        if self.bid_one.is_double:
            bid = self._rebid_after_double()
        elif self._advancer_bids_stayman():
            bid = self._response_to_stayman()
        elif self._can_bid_sevel_card_suit_at_level_three():
            bid = self.next_level_bid(self.longest_suit, '0795')
        elif self.suit_length(self.advancer_bid_one.denomination) >= 3:
            bid = self._support_for_partner()
        elif self.is_balanced and self.stoppers_in_bid_suits:
            bid = self._balanced_rebid()
        elif self.shape[0] >= 7 and self.advancer_bid_one.level == 3:
            bid = self.next_level_bid(self.bid_one.denomination, '0747')
        elif self._has_long_strong_suit():
            bid = self.next_level_bid(self.bid_one.denomination, '0748')
        elif self._has_five_four_and_can_bid_second_suit():
            bid = self.next_level_bid(self.second_suit, '0746')
        elif self._can_show_four_card_suit_at_level_two():
            bid = self.next_level_bid(self.second_suit, '0940')
        elif self._can_show_four_card_suit_at_level_four():
            bid = self.next_level_bid(self.second_suit, '0368')
        elif self._has_six_card_suit_and_no_support_for_advancer():
            if self.shape[0] >= 7:
                level = 1
            elif ((self.suit_length(self.advancer_bid_one.denomination) >= 2 and
                    self.advancer_bid_one.denomination.rank > self.bid_one.denomination.rank) or
                    self.hcp <= 12):
                level = 0
            else:
                level = 1
            bid = self.next_level_bid(self.bid_one.denomination, '0749', raise_level=level)
        elif self._can_bid_five_five_at_level_two():
            bid = self.next_level_bid(self.second_suit, '0750')
        elif self._can_bid_seven_card_suit_at_level_three():
            bid = self.next_level_bid(self.bid_one.denomination, '0751')
        elif self.my_last_bid.is_nt:
            bid = Pass('0744')
        elif self._has_twelve_points_no_support_for_advancer():
            bid = self.next_nt_bid('0752')
        elif self._good_second_suit_and_rebiddable_long_suit():
            bid = self.next_level_bid(self.second_suit, '0920')
        elif self.shape[0] >= 6 and self.longest_suit not in self.opponents_suits:
            bid = self.next_level_bid(self.longest_suit, '0000')
        else:
            bid = Pass('0753')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _partner_shows_support(self):
        """Bid after partner has shown support."""
        hvp = self.hcp + self.distribution_points
        if self.hcp >= 19:
            bid = self.next_level_bid(self.bid_one.denomination, '0754', raise_level=1)
        elif hvp >= 16 and self.bid_one.denomination.is_major:
            bid = self.next_level_bid(self.bid_one.denomination, '0755')
        else:
            bid = self._partner_shows_support_weak_hand()
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _partner_shows_support_weak_hand(self):
        """Bid after partner has shown support with weak hand."""
        if self._advancer_has_jumped_not_competitive():
            bid = self._partner_shows_support_with_jump()
        elif self._advancer_has_bid_at_level_three():
            bid = self.suit_bid(4, self.bid_one.denomination, '0756')
        elif self._advancer_has_jumped_over_openers_rebid():
            bid = self.next_level_bid(self.bid_one.denomination, '0758')
        elif self.six_four and self.next_level(self.bid_one.denomination) <= 3 and self.hcp >= 11:
            bid = self.next_level_bid(self.bid_one.denomination, '0759')
        elif (self._has_thirteen_points_and_can_bid_five_card_suit_at_level_three() and
                not self.bid_history[-1] == 'P'):
            bid = self.next_level_bid(self.bid_one.denomination, '0760')
        elif self._has_eleven_points_and_can_bid_seven_card_suit_at_level_three():
            bid = self.next_level_bid(self.bid_one.denomination, '0761')
        elif self._has_fifteen_points_can_bid_major():
            bid = self.next_level_bid(self.bid_one.denomination, '0762')
        else:
            bid = Pass('0763')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _partner_shows_support_with_jump(self):
        """Bid after partner has shown support with a jump."""
        level = self.next_level(self.bid_one.denomination)
        level += 1
        if self.bid_one.denomination.is_major:
            level = min(4, level)
        else:
            level = min(5, level)
        if self._can_raise_after_advancer_jumps(level):
            bid = self.suit_bid(level, self.bid_one.denomination, '0764')
        else:
            bid = Pass('0765')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _support_for_partner(self):
        """Bid with support for partner."""
        level = self._get_level_with_support_for_advancer()
        if self._advancer_has_bid_clubs_and_can_support(level):
            bid = self.suit_bid(level, self.advancer_bid_one.denomination, '0766')
        else:
            bid = Pass('0767')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _response_to_stayman(self):
        """Bid after partner has used Stayman"""
        if self.hearts >= 4 and self.heart_suit not in self.opponents_suits:
            bid = self.next_level_bid(self.heart_suit, '0768')
        elif self.spades >= 4 and self.spade_suit not in self.opponents_suits:
            bid = self.next_level_bid(self.spade_suit, '0769')
        elif self.next_level(self.diamond_suit) <= 2:
            bid = self.diamond_bid(2, '0237')
        elif self.nt_level <= 3:
            bid = self.nt_bid(3, '0770')
        else:
            bid = Pass('0000')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _no_support_for_partner(self, suit):
        """Bid with no support for partner."""
        level = self.next_level(suit)
        if level <= self.suit_length(suit) or self.advancer_bid_one.level == 3:
            bid = self.suit_bid(level, suit, '0771')
        else:
            bid = Pass('0772')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _balanced_rebid(self):
        """Bid with balanced hand."""
        if self.my_last_bid.is_nt:
            bid = self._balanced_overcall_nt()
        else:
            bid = self._balanced_rebid_after_suit()
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _balanced_overcall_nt(self):
        """Return bid with a balanced hand after overcaller bid NT."""
        if (self.advancer_bid_one.denomination == self.club_suit and
                Bid(self.bid_history[-1]).is_pass):
            bid = self._response_to_stayman()
        elif (self.my_last_bid.level >= 2 and
              self.suit_length(self.advancer_bid_one.denomination) >= 2):
            bid = self.next_level_bid(self.advancer_bid_one.denomination, '0773')
        else:
            bid = Pass('0774')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    def _balanced_rebid_after_suit(self):
        """Rebid with balanced hand after suit bid."""
        if (self.advancer_bid_one.level == 3 and
                self.hcp >= 14 and
                self.nt_level <= 3):
            bid = self.nt_bid(3, '0775')
        elif self.hcp >= 14 and self.nt_level <= 2:
            bid = self.nt_bid(2, '0776')
        else:
            bid = Pass('0777')
        self.tracer(__name__, inspect.currentframe(), bid, self.trace)
        return bid

    # Various utility functions

    def _cheapest_four_card_suit(self):
        """Return the cheapest 4 card suit."""
        suits = []
        for suit in self.suits:
            if self.suit_length(suit) == 4:
                suits.append(suit)
        cheapest = None
        for suit in suits:
            if cheapest:
                if suit < cheapest:
                    cheapest = suit
            else:
                cheapest = suit
        return cheapest

    def _biddable_five_card_major(self):
        """Return a biddable 5 card major."""
        suit = None
        if (self.hearts >= 5 and
                self.heart_suit not in self.opponents_suits):
            suit = self.heart_suit
        elif (self.spades >= 5 and
              self.spade_suit not in self.opponents_suits):
            suit = self.spade_suit
        return suit

    def _five_five_second_suit(self):
        """Return second suit in five/five hands."""
        if self.bid_one.is_suit_call:
            suit_one = self.bid_one.denomination
        else:
            suit_one = self.longest_suit
        if suit_one == self.longest_suit:
            suit_two = self.second_suit
        else:
            suit_two = self.second_suit
        if suit_two in self.opponents_suits:
            suit = suit_one
        elif suit_one in self.opponents_suits:
            suit = suit_two
        else:
            suit = suit_two
        return suit

    def _get_overcallers_level(self):
        """Return the level at which overcaller has bid."""
        if self.bid_one. is_value_call:
            suit = self.bid_one.denomination
            overcallers_level = self.next_level(suit)
        else:
            overcallers_level = 0
        return overcallers_level

    def _get_best_suit_for_rebid(self):
        """Return best own suit."""
        suit = self.longest_suit
        if self.five_five:
            suit = self.cheaper_suit(self.longest_suit, self.second_suit)
        return suit

    def _has_opponents_suit(self, opponents_bid):
        """Return True if hand has 4+ in opponents suit."""
        value = False
        if Bid(opponents_bid).is_suit_call:
            suit = Bid(opponents_bid).denomination
            if (self.suit_length(suit) >= 4 and
                    self.suit_points(suit) >= 4):
                value = True
            elif self.suit_length(suit) >= 5:
                value = True
        return value

    def _select_suit_for_rebid(self):
        """Select best suit for rebid."""
        suit_for_rebid = self.longest_suit
        if (self.advancer_bid_one.denomination.is_major and
                self.suit_length(self.advancer_bid_one.denomination) >= 4):
            suit = self.advancer_bid_one.denomination
        elif (self.opener_bid_one.denomination == suit_for_rebid or
              self.responder_bid_one.denomination == suit_for_rebid):
            suit = self.second_suit
        else:
            suit = suit_for_rebid
        return suit

    def _get_level_with_support_for_advancer(self):
        """Return the level to bid if overcaller can support advancer."""
        level = self.next_level(self.advancer_bid_one.denomination)
        if self._is_strong_or_advancer_has_jumped():
            level += 1
        if self.advancer_bid_one.denomination.is_major:
            level = min(level, 4)
        return level

    # Various boolean functions

    def _can_double(self):
        """Return True if hand is suitable for DOUBLE."""
        value = False
        overcallers_level = self._get_overcallers_level()
        opponents_agreed_suit = self.openers_agreed_suit()
        if opponents_agreed_suit:
            if (opponents_agreed_suit.is_suit and
                    not self.bid_one.is_pass and
                    self.advancer_bid_one.is_pass and
                    self.shape in [[4, 4, 4, 1], [5, 4, 4, 0]] and
                    not self.responder_bid_one.is_game and
                    not self.opener_bid_two.is_game and
                    self.next_level(self.spade_suit) <= 4 and
                    (overcallers_level <= 3 and
                     opponents_agreed_suit != self.spade_suit)):
                value = True
        if self.opener_bid_two.is_nt:
            value = False
        return value

    def _very_strong_six_card_suit_advancer_bids_game(self):
        """Return True if very strong, six card suit and advancer bids over responder."""
        result = (self.my_last_bid.is_double and
                  self.responder_bid_one.is_value_call and
                  self.advancer_bid_one.is_game and
                  self.hcp >= 23 and
                  self.shape[0] >= 6 and
                  self.next_level(self.longest_suit) <= 6)
        return result

    def _advancer_supports_overcaller_suit(self):
        """Return True if advancer support overcaller."""
        result = (self.bid_one.denomination == self.advancer_bid_one.denomination and
                  self.bid_one.is_suit_call)
        return result

    def _has_long_suit(self):
        """Return True with long suit."""
        level = self.next_level(self.longest_suit)
        result = (self.shape[0] >= 7 or
                  (self.shape[0] >= 6 and level <= 2))
        return result

    def _can_rebid_longest_suit_at_level_two(self):
        """Return True if able to rebid longest suit."""
        result = (self.hcp >= 12 and
                  not self.bid_one.is_pass and
                  self.suit_length(self.longest_suit) >= 5 and
                  self.next_level(self.longest_suit) <= 2 and
                  self.suit_points(self.longest_suit) >= 6 and
                  self.longest_suit not in self.opponents_suits and
                  self.responder_bid_one.is_pass and
                  not self.opener_bid_two.is_nt and
                  self.opener_bid_one.denomination == self.opener_bid_two.denomination)
        return result

    def _can_bid_second_suit_at_level_two(self):
        """Return True if able to bid second suit."""
        result = (self.hcp >= 12 and
                  not self.bid_one.is_pass and
                  self.suit_length(self.longest_suit) >= 5 and
                  self.suit_length(self.second_suit) >= 4 and
                  self.second_suit.rank < self.longest_suit.rank and
                  self.next_level(self.second_suit) <= 2 and
                  self.suit_points(self.second_suit) >= 2 and
                  self.second_suit not in self.opponents_suits and
                  self.responder_bid_one.is_pass and
                  not self.opener_bid_two.is_nt and
                  self.opener_bid_one.denomination == self.opener_bid_two.denomination)
        return result

    def _can_rebid_second_suit_at_level_two(self):
        """Return True if second suit is suitable for a rebid."""
        result = (self.hcp >= 14 and
                  self.next_level(self.second_suit) <= 2 and
                  self.five_four and
                  self.second_suit not in self.opponents_suits)
        return result

    def _can_rebid_nt_at_three_level(self):
        """Return True if can rebid nt at 3 level."""
        result = (self.bid_one.name != '1NT' and
                  self.advancer_bid_one.name == '2NT' and
                  self.hcp >= 14 and
                  self.nt_level <= 3)
        return result

    def _is_competitive_auction(self):
        """Return True if competitive auction."""
        result = (self.opener_bid_two.is_value_call or
                  self.responder_bid_one.is_value_call or
                  self.opener_bid_one.level > 1)
        return result

    def _strong_with_biddable_five_card_major(self):
        """Return True if strong with biddable 5 card major."""
        result = (self.five_card_major_or_better and
                  self.hcp >= 15 and
                  self._biddable_five_card_major())
        return result

    def _strong_and_advancer_bids_two_nt(self):
        """Return True if strong and advancer bids 2NT."""
        result = (self.advancer_bid_one.name == '2NT' and
                  self.hcp >= 15 and
                  self.nt_level <= 3)
        return result

    def _can_show_second_suit_after_advancer_has_bid(self):
        """Return True if can bid second suit and advancer has bid."""
        result = (self.shape[1] == 4 and
                  self.suit_points(self.second_suit) >= 5 and
                  self.second_suit not in self.opponents_suits and
                  not self.advancer_bid_one.is_pass)
        return result

    def _can_bid_six_card_suit_in_competitive_auction(self):
        """Return True if can bid 6 card suit in competitive auction."""
        result = (self.last_bid.is_value_call and
                  self.shape[0] >= 6 and
                  self.suit_points(self.longest_suit) >= 9 and
                  self.next_level(self.longest_suit) <= 3 and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _can_rebid_suit_after_advancer_has_bid(self):
        """Return True if advancer bids and can repeat suit."""
        result = (self.hcp + self.shape[0] >= 16 and
                  (self.next_level(self.bid_one.denomination) <= 3 or
                   (self.shape[0] >= 7 and
                    self.advancer_bid_one.is_value_call)))
        return result

    def _weak_hand_after_opener_bids_weak_two(self):
        """Return True if opener bid weak two and moderate hand."""
        result = (self.opener_bid_one.level > 1 and
                  ((self.hcp <= 15 and self.shape[0] <= 5) or
                   (self.hcp <= 14 and self.shape[0] <= 6)) and
                  not self.responder_bid_one.is_value_call)
        return result

    def _strong_and_no_support_for_advancer(self, suit_for_rebid):
        """Return True if strong and no support for advancer."""
        result = (self.hcp >= 16 and
                  self.shape[0] >= 5 and
                  suit_for_rebid.is_major and
                  self.suit_length(self.advancer_bid_one.denomination) <= 3 and
                  suit_for_rebid not in self.opponents_suits and
                  self.next_level(suit_for_rebid) <= 3)
        return result

    def _very_strong_and_can_bid_nt(self):
        """Return True if very strong and can bid NT."""
        result = (self.hcp >= 20 and
                  self.advancer_bid_one.denomination.is_minor and
                  self.is_semi_balanced and
                  self.stoppers_in_bid_suits and
                  self.next_level(self.no_trumps) <= 3)
        return result

    def _can_support_advancer_after_double(self):
        """Return True if can support advancer."""
        result = (self.suit_length(self.advancer_bid_one.denomination) >= 3 and
                  not (self.shape[0] >= 6 and
                       self.longest_suit != self.advancer_bid_one.denomination))
        return result

    def _suit_for_rebid_is_minor_after_double(self, suit_for_rebid):
        """Return True if rebid suit is minor and can support advancer."""
        result = (suit_for_rebid.is_minor and
                  self.advancer_bid_one.level >= 2 and
                  self.advancer_bid_one.denomination.is_major and
                  self.suit_length(self.advancer_bid_one.denomination) >= 3)
        return result

    def _strong_and_can_bid_rebid_suit(self, suit_for_rebid):
        """Return True if strong and can rebid suit."""
        result = (self.hcp >= 15 and self.shape[0] >= 5 and
                  self.suit_points(suit_for_rebid) >= 5 and
                  suit_for_rebid not in self.opponents_suits and
                  (self.opener_bid_one.level == 2 or
                   self.next_level(suit_for_rebid) <= 2))
        return result

    def _can_bid_five_card_major_at_three_level(self):
        """Return True if 5 card major at 3 level."""
        result = (self.longest_suit.is_major and
                  self.shape[0] >= 5 and
                  self.next_level(self.longest_suit) <= 3 and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _strong_balanced_and_advancer_bids_minor(self):
        """Return True if strong, balanced and advancer bids minor."""
        result = (self.hcp >= 17 and
                  not (self.bid_one.is_double and self.overcaller_in_fourth_seat) and
                  self.advancer_bid_one.denomination.is_minor and
                  self.is_balanced and
                  self.stoppers_in_bid_suits and
                  self.nt_level <= 3)
        return result

    def _above_minimum_and_advancer_bids_after_double(self):
        """Return True if above minimum and advancer at level two."""
        result = (self._strong_or_competitive_after_double() and
                  (self._jump_after_double() or self.responder_bid_one.is_pass) and
                  (self.hcp >= 14 or self.opener_bid_two.is_value_call) and
                  self.suit_length(self.advancer_bid_one.denomination) >= 4)
        return result

    def _strong_or_competitive_after_double(self):
        """Return True if strong  or competitive."""
        competitive_auction = Bid(self.bid_history[-1]).is_value_call
        result = (self.hcp >= 13 and competitive_auction and
                  (self.advancer_bid_one.level >= 3 or
                   self.suit_length(self.advancer_bid_one.denomination) >= 4) or
                  self.hcp >= 16)
        return result

    def _jump_after_double(self):
        """Return True if advancer has jumped after a double."""
        last_bid = None
        for bid in self.bid_history:
            if Bid(bid).is_value_call:
                last_bid = Bid(bid)
            if bid == 'D':
                break
        jump_steps = self.levels_to_bid(last_bid, self.advancer_bid_one)
        if jump_steps > 1:
            return True
        else:
            return False

    def _is_balanced_with_stopper(self, suit_for_rebid):
        """Return True if _balanced_with_stoppers."""
        result = (self.stoppers_in_bid_suits and
                  self.shape[0] == 4 and
                  suit_for_rebid.is_minor and
                  self.nt_level <= 3)
        return result

    def _four_card_support_for_advancers_major(self):
        """Return True if 4 card support for advancer."""
        result = (self.advancer_bid_one.denomination.is_major and
                  self.suit_length(self.advancer_bid_one.denomination) >= 4 or
                  (self.responder_bid_one.is_value_call and
                   self.suit_length(self.advancer_bid_one.denomination) == 3))
        return result

    def _can_bid_five_card_major_at_two_level(self, suit_for_rebid):
        """Return True if can bid 5 card major at two level."""
        result = (self.is_balanced and
                  suit_for_rebid.is_major and
                  self.suit_length(self.longest_suit) >= 5 and
                  self.next_level(suit_for_rebid) <= 2)
        return result

    def _has_five_card_suit_and_no_support_from_advancer(self, suit_for_rebid):
        """Return True if 5 card suit and no support from advancer."""
        result = (self.advancer_bid_one.denomination != suit_for_rebid and
                  self.shape[0] >= 5)
        return result

    def _is_balanced_and_long_suit_is_minor(self, suit_for_rebid):
        """Return True if suit is minor and balanced."""
        result = (suit_for_rebid.is_minor and
                  self.is_balanced and
                  self.stoppers_in_bid_suits)
        return result

    def _has_three_card_support_for_advancers_major(self, suit_for_rebid):
        """Return True if 3 card support for advancers suit."""
        result = (suit_for_rebid.is_minor and
                  self.advancer_bid_one.denomination.is_major and
                  self.suit_length(self.advancer_bid_one.denomination) >= 3)
        return result

    def _strong_and_opposition_weak(self):
        """Return True if 16 points and opposition weak."""
        result = (self.hcp >= 16 and
                  self.next_level(self.longest_suit) <= 3 and
                  self.opener_bid_two.is_pass and
                  self.opener_bid_one.is_suit_call and
                  not self.responder_bid_one.is_nt and
                  not self.five_five)
        return result

    def _is_strong_has_five_five(self):
        """Return True if strong with 5/5."""
        result = (self.hcp >= 16 and
                  self.five_five and
                  self.next_level(self.longest_suit) <= 3 and
                  (self.longest_suit not in self.opponents_suits or
                   self.second_suit not in self.opponents_suits))
        return result

    def _is_strong_with_good_five_card_suit(self):
        """Return True if strong with good 5 card suit."""
        result = (self.hcp >= 15 and
                  self.shape[0] >= 5 and
                  self.suit_points(self.longest_suit) >= 3 and
                  self.next_level(self.longest_suit) <= 3 and
                  self.longest_suit not in self.opponents_suits and
                  (self.advancer_bid_one.is_value_call or
                   self.next_level(self.longest_suit) <= 2 or
                   self.hcp >= 19))
        return result

    def _is_strong_and_balanced(self):
        """Return True if strong and balanced."""
        result = (self.hcp >= 18 and
                  self.is_balanced and
                  self.nt_level <= 2 and
                  self.responder_bid_one.level == 1 and
                  self.stoppers_in_bid_suits)
        return result

    def _is_medium_and_balanced(self):
        """Return True if medium balanced."""
        result = (self.hcp >= 16 and
                  self.is_balanced and
                  self.nt_level <= 2 and
                  not self.opener_bid_one.is_nt and
                  self.responder_bid_one.is_pass and
                  self.stoppers_in_bid_suits)
        return result

    def _advancer_bids_stayman(self):
        """Return True if advancer bids stayman."""
        result = (self.bid_one.name == '1NT' and
                  self.advancer_bid_one.denomination == self.club_suit and
                  not Bid(self.bid_history[-3]).is_value_call)
        return result

    def _has_long_strong_suit(self):
        """Return True if long strong suit."""
        result = (self.suit_points(self.longest_suit) >= 5 and
                  (self.shape[0] >= 6 and self.hcp >= 13) or
                  (self.shape[0] >= 7 and self.hcp >= 12))
        return result

    def _has_five_four_and_can_bid_second_suit(self):
        """Return True if 5/4 and can bid second suit."""
        result = (self.five_four and
                  self.advancer_bid_one.level >= 2 and
                  self.hcp >= 12 and
                  self.next_level(self.second_suit) <= 2 and
                  self.second_suit not in self.opponents_suits)
        return result

    def _has_six_card_suit_and_no_support_for_advancer(self):
        """Return True if six card suit and no support for advancer."""
        result = (self.shape[0] >= 6 and
                  self.suit_length(self.advancer_bid_one.denomination) <= 2 and
                  self.bid_one.denomination.is_major and
                  self.next_level(self.bid_one.denomination) <= 3)
        return result

    def _can_bid_five_five_at_level_two(self):
        """Return True if 5/5 at level 2."""
        result = (self.five_five and
                  self.advancer_bid_one.is_suit_call and
                  self.next_level(self.second_suit) <= 2 and
                  self.second_suit not in self.opponents_suits)
        return result

    def _can_bid_seven_card_suit_at_level_three(self):
        """Return True if can bid 7 card suit at level 3."""
        result = (self.shape[0] >= 7 and
                  self.advancer_bid_one.is_value_call and
                  self.next_level(self.bid_one.denomination) <= 3)
        return result

    def _has_twelve_points_no_support_for_advancer(self):
        """Return True if 12 points and no support for advancer."""
        result = (self.advancer_bid_one.level >= 2 and
                  self.suit_length(self.advancer_bid_one.denomination) <= 1 and
                  self.hcp >= 12 and
                  self.nt_level <= 3)
        return result

    def _advancer_has_jumped_not_competitive(self):
        """Return True if advancer has jumped and not competitive."""
        result = (self.hcp >= 13 and
                  (self.is_jump(Bid(self.bid_history[-3]), self.advancer_bid_one) or
                   (self.is_jump(self.bid_one, self.advancer_bid_one) and
                    Bid(self.bid_history[-3]).is_pass)))
        return result

    def _advancer_has_bid_at_level_three(self):
        """Return True if advancer bids at level 3."""
        result = (self.advancer_bid_one.level == 3 and
                  self.hcp >= 14 and
                  self.longest_suit.is_major and
                  not self.partner_has_passed and
                  self.next_level(self.bid_one.denomination) <= 4)
        return result

    def _advancer_has_jumped_over_openers_rebid(self):
        """Return True if advancer has jumped over opener bid two."""
        result = (self.is_jump(self.opener_bid_two, self.advancer_bid_one) and
                  self.hcp >= 11 and
                  self.opener_bid_two.is_suit_call and
                  self.next_level(self.longest_suit) <= 4)
        return result

    def _has_thirteen_points_and_can_bid_five_card_suit_at_level_three(self):
        """Return True if 13 points and can bid 5 card suit at 3 level."""
        result = (self.hcp >= 13 and
                  self.shape[0] >= 5 and
                  self.next_level(self.longest_suit) <= 3 and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _has_eleven_points_and_can_bid_seven_card_suit_at_level_three(self):
        """Return True if 11 points and can bid 7 card suit at 3 level."""
        result = (self.hcp >= 11 and
                  self.shape[0] >= 7 and
                  self.next_level(self.bid_one.denomination) <= 3)
        return result

    def _has_fifteen_points_can_bid_major(self):
        """Return True if strong and can bid major."""
        result = (self.support_points(self.bid_one.denomination) >= 15 and
                  self.bid_one.denomination.is_major and
                  self.bid_one.denomination not in self.opponents_suits)
        return result

    def _can_raise_after_advancer_jumps(self, level):
        """Return True if can bid again after advancer has jumped."""
        result = (not self.is_insufficient_bid(self.suit_bid(level, self.bid_one.denomination)) and
                  self.bid_one.denomination not in self.opponents_suits)
        return result

    def _can_attempt_support(self, level):
        """Return True if can attempt to support advancer."""
        result = (level <= self.suit_length(self.advancer_bid_one.denomination) or
                  self.hcp >= 19 or
                  self.advancer_bid_one.level == 3 or
                  self.is_jump(self.my_last_bid, self.advancer_bid_one))
        return result

    def _advancer_has_bid_clubs_and_can_support(self, level):
        """Return True if advancer has bid clubs."""
        result = (level >= self.next_level(self.advancer_bid_one.denomination) and
                  not (self.my_last_bid.is_nt and
                  self.advancer_bid_one.denomination == self.club_suit) and
                  self.support_points(self.advancer_bid_one.denomination) >= 13 and
                  self._can_attempt_support(level))
        return result

    def _is_strong_or_advancer_has_jumped(self):
        """Return True if strong or advancer has jumped."""
        result = (self.hcp >= 17 or
                  (self.suit_length(self.advancer_bid_one.denomination) >= 4 and
                   self.support_shape_points(self.advancer_bid_one.denomination) >= 3) or
                  (self.is_jump(self.my_last_bid, self.advancer_bid_one) and
                   self.advancer_bid_one.denomination.is_major))
        return result

    def _can_show_four_card_suit_at_level_two(self):
        """Return True if can show four card suit at level 4."""
        result = (self.opener_bid_one.is_suit_call and
                  self.shape[0] >= 6 and
                  self.shape[1] >= 4 and
                  self.next_level(self.second_suit) <= 2 and
                  self.longest_suit not in self.opponents_suits and
                  self.second_suit not in self.opponents_suits)
        return result

    def _can_show_four_card_suit_at_level_four(self):
        """Return True if can show four card suit at level 4."""
        result = (self.opener_bid_one.is_suit_call and
                  self.shape[1] >= 4 and
                  3 <= self.next_level(self.second_suit) <= 4 and
                  self.longest_suit not in self.opponents_suits and
                  self.second_suit not in self.opponents_suits)
        return result

    def _is_strong_in_opponents_suit(self):
        """Return True if strong in opponents suit."""
        result = (self.suit_length(self.last_bid.denomination) >= 4 and
                  self.suit_points(self.last_bid.denomination) >= 4)
        return result

    def _is_weak_and_some_support_for_advancer(self, suit_for_rebid):
        """Return True if weak and some support for partner."""
        result = (self.hcp <= 16 and
                  self.advancer_bid_one.level >= 2 and
                  self.suit_length(self.advancer_bid_one.denomination) >= 2 and
                  self.last_bid.is_pass and
                  self.next_level(suit_for_rebid) <= 2)
        return result

    def _advancer_bids_three_nt_and_long_suit(self):
        """Return True if advancer has bid 3NT and long suit."""
        suit = self.longest_suit
        result = (self.advancer_bid_one.name == '3NT' and
                  self.shape[0] >= 7 and
                  self.game_level(suit) >= self.next_level(suit) and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _advancer_bids_two_nt_and_six_card_suit_and_weak(self):
        """Return True if advancer has bid 2NT and single suited and weak."""
        result = (self.advancer_bid_one.name == '2NT' and
                  self.shape[0] >= 6 and
                  self.hcp <= 9 and
                  self.longest_suit not in self.opponents_suits)
        return result

    def _partner_weak_after_double(self):
        """Return True if partner weak and balanced."""
        result = ((self.partner_bids_at_lowest_level() or self.hcp < 19) and
                  Bid(self.bid_history[-1]).is_pass and
                  not self.four_four_four_one)
        return result

    def _can_raise_advancer_after_double(self):
        """Return True if can raise advancer after a double."""
        advancer_not_weak = ((self.my_last_bid.level == 2 and
                             not self.partner_bids_at_lowest_level()) or
                             self.opener_bid_one.is_nt)
        result = (self.hcp >= 16 and
                  advancer_not_weak and
                  self.right_hand_bid.is_pass and
                  not self.next_level_bid(self.advancer_bid_one.denomination).is_game)
        return result

    def _can_bid_second_suit(self):
        """Return True if can bid second suit."""
        result = (self.shape[1] >= 5 and
                  self.next_level(self.second_suit) <= 2 and
                  self.second_suit not in self.opponents_suits)
        return result

    def _strong_over_weak_three(self):
        """Return True if strong over weak 3."""
        result = (self.hcp >= 20 and self.opponents_at_game and
                  self.opener_bid_one.level == 3 and
                  self.suit_points(self.opener_bid_one.denomination) >= 4)
        return result

    def _support_for_partners_level_three_call(self):
        """Return True if Support for partners level 3 bid."""
        result = (self.partner_bid_one.level == 3 and
                  self.suit_length(self.partner_bid_one.denomination) >= 3 and
                  self.bid_history[-3] != 'P')
        return result

    def _can_bid_sevel_card_suit_at_level_three(self):
        """Return True if can bid a 7 card suit at level 3."""
        result = (self.shape[0] >= 7 and 
                  self.hcp <= 9 and
                  self.next_level(self.longest_suit) <= 3 and 
                  self.longest_suit not in self.opponents_suits)
        return result

    def _very_strong_and_some_support_for_partner(self):
        """Return True if very strong and some support for partner."""
        result = (self.hcp >= 23 and 
                  ((self.partner_last_bid.denomination.is_major and 
                    self.suit_length(self.partner_last_bid.denomination) >= 2) or 
                  ((self.partner_last_bid.denomination.is_minor and 
                    self.suit_length(self.partner_last_bid.denomination) >= 4))))
        return result

    def _minimum_after_double_over_1nt(self):
        """Return True if minimum after double over 1NT."""
        result = (self.opener_bid_one.name == '1NT' and
                  self.hcp == 16 and
                  self.responder_bid_one.is_value_call and
                  self.advancer_bid_one.level >= 3)
        return result

    def _good_second_suit_and_rebiddable_long_suit(self):
        """Return True if good second suit and rebiddable first suit."""
        result = (self.shape[1] >= 4 and 
                  self.suit_points(self.longest_suit) >= 4  and 
                  self.suit_points(self.second_suit) >= 5 and 
                  self.second_suit.rank < self.longest_suit.rank and
                  self.second_suit not in self.opponents_suits)
        return result

    # def xxx(self):
    #     """Return True if zzz."""
    #     result = False
    #     return result

    # def xxx(self):
    #     """Return True if zzz."""
    #     result = False
    #     return result
