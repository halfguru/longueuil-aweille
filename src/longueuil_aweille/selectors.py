from dataclasses import dataclass


@dataclass
class SearchSelectors:
    keyword_search: str
    search_option_or: str
    available_only_radio: str
    search_all_radio: str
    search_button: str


@dataclass
class CartSelectors:
    cart_button: str
    dossier_input_template: str
    nip_input_template: str
    unregister_button_template: str
    validate_button: str
    result_container: str = "body"


@dataclass
class BrowseSelectors:
    search_button: str
    activity_rows: str
    pagination_links: str


@dataclass
class VerifySelectors:
    carte_acces_input: str
    telephone_input: str
    submit_button: str


DEFAULT_SEARCH_SELECTORS = SearchSelectors(
    keyword_search="#ctlBlocRecherche_ctlMotsCles_ctlMotsCle",
    search_option_or="#ctlBlocRecherche_ctlMotsCles_ctlOptionOU",
    available_only_radio="input[name*='ctlSelDisponibilite'][value='ctlDispoSeulement']",
    search_all_radio="input[name*='ctlSelDisponibilite'][value='ctlToutes']",
    search_button="#ctlBlocRecherche_ctlRechercher",
)

DEFAULT_CART_SELECTORS = CartSelectors(
    cart_button="#ctlGrille_ctlMenuActionsBas_ctlAppelPanierIdent",
    dossier_input_template="#ctlPanierActivites_ctlActivites_ctl{i:02d}_ctlRow_ctlListeIdentification_ctlListe_itm0_ctlBloc_ctlDossier",
    nip_input_template="#ctlPanierActivites_ctlActivites_ctl{i:02d}_ctlRow_ctlListeIdentification_ctlListe_itm0_ctlBloc_ctlNip",
    unregister_button_template="#ctlPanierActivites_ctlActivites_ctl{i:02d}_ctlRow_ctlListeIdentification_ctlListe_itm0_ctlBloc_ctlMoins",
    validate_button="#ctlMenuActionBas_ctlAppelPanierConfirm",
)

DEFAULT_BROWSE_SELECTORS = BrowseSelectors(
    search_button="#ctlBlocRecherche_ctlRechercher",
    activity_rows="tr",
    pagination_links="a[id*='ctlLienPage']",
)

DEFAULT_VERIFY_SELECTORS = VerifySelectors(
    carte_acces_input="input[name='numero']",
    telephone_input="input[name='telephone']",
    submit_button="input[name='action'][type='submit']",
)
