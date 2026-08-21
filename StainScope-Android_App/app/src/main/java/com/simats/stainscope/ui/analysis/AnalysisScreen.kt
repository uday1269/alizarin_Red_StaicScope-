package com.simats.stainscope.ui.analysis

import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.outlined.CompareArrows
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.material3.TabRowDefaults.tabIndicatorOffset
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import com.simats.stainscope.ui.components.StainScopeButton
import com.simats.stainscope.ui.components.StainScopeTextField
import com.simats.stainscope.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnalysisScreen(
    onNavigateToDashboard: () -> Unit,
    onNavigateToCompare: () -> Unit,
    onNavigateToReports: () -> Unit,
    onNavigateToProfile: () -> Unit,
    onNavigateBack: () -> Unit,
    onStartAnalysis: (Uri, String, String, String) -> Unit,
    viewModel: AnalysisViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var visible by remember { mutableStateOf(false) }
    val context = LocalContext.current

    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        viewModel.onImageSelected(uri)
    }

    LaunchedEffect(uiState.isSuccess) {
        if (uiState.isSuccess) {
            val uri = uiState.selectedImageUri
            if (uri != null) {
                onStartAnalysis(
                    uri,
                    uiState.sampleFileName,
                    uiState.cellLine,
                    "${uiState.incubationPeriod} | ${uiState.magnification}"
                )
            }
            viewModel.resetState()
        }
    }

    LaunchedEffect(uiState.error) {
        uiState.error?.let {
            Toast.makeText(context, it, Toast.LENGTH_LONG).show()
            viewModel.clearError()
        }
    }

    LaunchedEffect(Unit) {
        visible = true
    }

    Scaffold(
        topBar = {
            Column(modifier = Modifier.background(MaterialTheme.colorScheme.surface)) {
                TopAppBar(
                    title = { 
                        Text(
                            text = "Analysis Workstation",
                            fontWeight = FontWeight.Black, 
                            fontSize = 22.sp
                        ) 
                    },
                    navigationIcon = {
                        IconButton(onClick = onNavigateBack) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack, 
                                contentDescription = "Back"
                            )
                        }
                    },
                    actions = {
                        IconButton(onClick = { }) {
                            Icon(Icons.Outlined.Notifications, contentDescription = "Notifications")
                        }
                        IconButton(onClick = onNavigateToProfile) {
                            Surface(
                                shape = CircleShape,
                                color = PrimaryMaroon.copy(alpha = 0.1f),
                                modifier = Modifier.size(38.dp)
                            ) {
                                Box(contentAlignment = Alignment.Center) {
                                    Text("SC", color = PrimaryMaroon, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                                }
                            }
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = MaterialTheme.colorScheme.surface,
                        titleContentColor = MaterialTheme.colorScheme.onSurface,
                        navigationIconContentColor = MaterialTheme.colorScheme.onSurface,
                        actionIconContentColor = MaterialTheme.colorScheme.onSurface
                    )
                )
                
                ScrollableTabRow(
                    selectedTabIndex = 1,
                    containerColor = MaterialTheme.colorScheme.surface,
                    contentColor = PrimaryMaroon,
                    edgePadding = 16.dp,
                    divider = {},
                    indicator = { tabPositions ->
                        if (tabPositions.size > 1) {
                            TabRowDefaults.SecondaryIndicator(
                                Modifier.tabIndicatorOffset(tabPositions[1]),
                                color = PrimaryMaroon,
                                height = 3.dp
                            )
                        }
                    }
                ) {
                    val tabs = listOf(
                        "Dashboard" to Icons.Outlined.Dashboard,
                        "Upload & Analyze" to Icons.Outlined.CloudUpload,
                        "Compare" to Icons.AutoMirrored.Outlined.CompareArrows,
                        "Reports" to Icons.Outlined.Description
                    )
                    tabs.forEachIndexed { index, pair ->
                        val isSelected = index == 1
                        Tab(
                            selected = isSelected,
                            onClick = { 
                                when(index) {
                                    0 -> onNavigateToDashboard()
                                    1 -> { /* Already here */ }
                                    2 -> onNavigateToCompare()
                                    3 -> onNavigateToReports()
                                }
                            },
                            text = { 
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    modifier = Modifier.padding(vertical = 12.dp)
                                ) {
                                    Icon(
                                        imageVector = pair.second,
                                        contentDescription = null,
                                        modifier = Modifier.size(16.dp),
                                        tint = if (isSelected) PrimaryMaroon else MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = pair.first, 
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                        fontSize = 13.sp,
                                        color = if (isSelected) PrimaryMaroon else MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            }
                        )
                    }
                }
                HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
            }
        }
    ) { padding ->
        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(animationSpec = tween(600)) + slideInVertically(initialOffsetY = { 60 })
        ) {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .background(MaterialTheme.colorScheme.background),
                contentPadding = PaddingValues(20.dp)
            ) {
                item(key = "quant_lab_header") {
                    Text(
                        text = "Quantification Lab",
                        fontSize = 32.sp,
                        fontWeight = FontWeight.Black,
                        color = MaterialTheme.colorScheme.onBackground,
                        lineHeight = 38.sp
                    )
                    Text(
                        text = "Upload Alizarin Red S stained micrograph for automated osteogenic quantification.",
                        fontSize = 15.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(top = 12.dp, bottom = 32.dp),
                        lineHeight = 22.sp
                    )
                }

                item(key = "upload_area_card") {
                    UploadArea(
                        selectedImageUri = uiState.selectedImageUri,
                        onBrowseClick = { launcher.launch("image/*") }
                    )
                    Spacer(modifier = Modifier.height(24.dp))
                }

                item(key = "metadata_section_card") {
                    MetadataSection(
                        fileName = uiState.sampleFileName,
                        onFileNameChange = viewModel::onFileNameChange,
                        cellLine = uiState.cellLine,
                        onCellLineChange = viewModel::onCellLineChange,
                        incubationPeriod = uiState.incubationPeriod,
                        onIncubationPeriodChange = viewModel::onIncubationPeriodChange,
                        magnification = uiState.magnification,
                        onMagnificationChange = viewModel::onMagnificationChange
                    )
                    Spacer(modifier = Modifier.height(32.dp))
                }
                
                item(key = "start_analysis_btn") {
                    Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                        if (uiState.isLoading) {
                            CircularProgressIndicator(color = PrimaryMaroon)
                        } else {
                            StainScopeButton(
                                text = "Start AI Stain Quantification",
                                onClick = {
                                    if (uiState.selectedImageUri != null && uiState.sampleFileName.isNotBlank()) {
                                        viewModel.startAnalysis()
                                    } else {
                                        Toast.makeText(context, "Please upload an image and enter experiment name", Toast.LENGTH_SHORT).show()
                                    }
                                }
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(48.dp))
                }
            }
        }
    }
}

@Composable
fun UploadArea(
    selectedImageUri: Uri?,
    onBrowseClick: () -> Unit
) {
    val dashColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.3f)
    val stroke = Stroke(width = 2.5f, pathEffect = PathEffect.dashPathEffect(floatArrayOf(20f, 15f), 0f)) 
    
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .height(260.dp)
            .shadow(4.dp, RoundedCornerShape(24.dp))
            .drawBehind {
                drawRoundRect(
                    color = dashColor,
                    style = stroke,
                    cornerRadius = CornerRadius(24.dp.toPx())
                )
            }
            .clip(RoundedCornerShape(24.dp))
            .clickable { onBrowseClick() },
        color = MaterialTheme.colorScheme.surface
    ) {
        if (selectedImageUri != null) {
            Box(modifier = Modifier.fillMaxSize()) {
                AsyncImage(
                    model = selectedImageUri,
                    contentDescription = "Selected Micrograph",
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )
                Surface(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(12.dp)
                        .size(32.dp)
                        .clickable { onBrowseClick() },
                    shape = CircleShape,
                    color = Color.Black.copy(alpha = 0.5f)
                ) {
                    Icon(
                        imageVector = Icons.Default.Edit,
                        contentDescription = "Change Image",
                        tint = Color.White,
                        modifier = Modifier.padding(6.dp)
                    )
                }
            }
        } else {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
                modifier = Modifier.padding(24.dp)
            ) {
                Surface(
                    modifier = Modifier.size(72.dp),
                    shape = RoundedCornerShape(20.dp),
                    color = MaterialTheme.colorScheme.primary.copy(alpha = 0.08f)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = Icons.Outlined.CloudUpload, 
                            contentDescription = null, 
                            tint = MaterialTheme.colorScheme.primary, 
                            modifier = Modifier.size(36.dp)
                        )
                    }
                }
                Spacer(modifier = Modifier.height(20.dp))
                Text(
                    "Upload Micrograph", 
                    fontWeight = FontWeight.ExtraBold, 
                    fontSize = 18.sp,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    "Select Alizarin Red S stained TIFF or PNG",
                    fontSize = 13.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(top = 4.dp, bottom = 24.dp)
                )
                
                Button(
                    onClick = onBrowseClick,
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryMaroon),
                    contentPadding = PaddingValues(horizontal = 24.dp, vertical = 12.dp)
                ) {
                    Text(
                        "Browse Laboratory Files", 
                        fontWeight = FontWeight.Bold, 
                        fontSize = 14.sp
                    )
                }
            }
        }
    }
}

@Composable
fun MetadataSection(
    fileName: String,
    onFileNameChange: (String) -> Unit,
    cellLine: String,
    onCellLineChange: (String) -> Unit,
    incubationPeriod: String,
    onIncubationPeriodChange: (String) -> Unit,
    magnification: String,
    onMagnificationChange: (String) -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Outlined.Info, 
                    contentDescription = null,
                    tint = PrimaryMaroon,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Sample Identification",
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp,
                    color = MaterialTheme.colorScheme.onSurface
                )
            }
            Spacer(modifier = Modifier.height(24.dp))
            
            StainScopeTextField(
                value = fileName,
                onValueChange = onFileNameChange,
                label = "Experiment Name",
                placeholder = "e.g. hMSC-BMP2-D21-P4"
            )
            Spacer(modifier = Modifier.height(20.dp))
            
            MetadataDropdown(
                label = "Cell Line",
                value = cellLine,
                options = listOf("hMSC (Human Mesenchymal Stem Cells)", "MC3T3-E1 Pre-osteoblasts", "Saos-2 Osteosarcoma", "Primary Osteoblasts"),
                onSelected = onCellLineChange
            )
            Spacer(modifier = Modifier.height(20.dp))
            
            Row(modifier = Modifier.fillMaxWidth()) {
                Box(modifier = Modifier.weight(1f)) {
                    MetadataDropdown(
                        label = "Incubation Period",
                        value = incubationPeriod,
                        options = listOf("Day 7", "Day 14", "Day 21", "Day 28"),
                        onSelected = onIncubationPeriodChange
                    )
                }
                Spacer(modifier = Modifier.width(16.dp))
                Box(modifier = Modifier.weight(1f)) {
                    MetadataDropdown(
                        label = "Magnification",
                        value = magnification,
                        options = listOf("4x Objective", "10x Objective", "20x Objective", "40x Objective"),
                        onSelected = onMagnificationChange
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            Surface(
                color = WarningOrange.copy(alpha = 0.1f),
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(1.dp, WarningOrange.copy(alpha = 0.3f))
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.AutoMode, 
                        contentDescription = null, 
                        tint = WarningOrange, 
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = "Neural engine calibrated for Alizarin Red S peak absorbance (~560nm).",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurface,
                        lineHeight = 18.sp
                    )
                }
            }
        }
    }
}

@Composable
fun MetadataDropdown(
    label: String,
    value: String,
    options: List<String>,
    onSelected: (String) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }

    Column {
        Text(
            text = label,
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface,
            modifier = Modifier.padding(bottom = 8.dp)
        )
        Box {
            Surface(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
                    .clickable { expanded = true },
                shape = RoundedCornerShape(12.dp),
                color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = value,
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.weight(1f)
                    )
                    Icon(
                        imageVector = Icons.Default.ExpandMore,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            DropdownMenu(
                expanded = expanded,
                onDismissRequest = { expanded = false },
                modifier = Modifier.fillMaxWidth(0.8f)
            ) {
                options.forEach { option ->
                    DropdownMenuItem(
                        text = { Text(option) },
                        onClick = {
                            onSelected(option)
                            expanded = false
                        }
                    )
                }
            }
        }
    }
}

val WarningOrange = Color(0xFFFFB300)
